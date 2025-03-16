import json
from dataclasses import dataclass, field
from functools import partial
from itertools import zip_longest
from pathlib import Path
from types import new_class
from uuid import uuid4

import requests

import pyttman
from pyttman.core.containers import MessageMixin, Reply
from pyttman.core.plugins.base import PyttmanPlugin, PyttmanPluginIntercept


@dataclass
class OpenAiRequestPayload:
    model: str
    system_prompt: str
    user_prompt: str

    def as_json(self):
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": self.user_prompt
                }
            ]
        }

@dataclass
class RagMemoryBank:
    """
    The OpenAiRagMemoryBank is a dataclass that holds
    the conversation history with a user, and the
    memories that the AI should remember.
    """
    file_path: Path
    memories: dict[str, list[str]] = field(default_factory=dict)

    def get_memories(self, key: str) -> list[str]:
        """
        Return the memories for a given key.
        """
        return self.memories.get(str(key), [])

    def append_memory(self, key: str, memory: str):
        """
        Append a memory to the memory bank.
        """
        key = str(key)
        if self.memories.get(str(key)) is None:
            self.memories[key] = [memory]
        else:
            self.memories[key].append(memory)

    def as_json(self):
        return {
            "memories": self.memories
        }

    def load_memories(self):
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.save()

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
            self.memories = data["memories"]

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            data = self.as_json()
            f.write(json.dumps(data, indent=4))

    def memories_as_str(self, key: str) -> str:
        """
        Return the memories as a string.
        """
        key = str(key)
        base = "These are your long term memories with this user: "
        return base + "\n".join(self.memories[key])


class OpenAIPlugin(PyttmanPlugin):
    """
    The OpenAIPlugin offers seamless integrations with the OpenAI API.
    Use the plugin to define pre-prompts that can be used to pre- or post
    process your message in your Pyttman application.

    An example is to use a pre-defined system prompt to correct spelling
    mistakes before the message is passed to the intent matching system.

    Another example is to use the GPT as a post-processor, to generate
    a response based on the intent matched by the Pyttman application.

    Or - use the GPT to generate a response from scratch, when no intent
    matches the user's message. This would be a great way to combine the
    rule-based intent matching system with an AI model.

    The plugin supports RAG: conversational mode. When this is enabled, the
    plugin will keep a conversation history for each user in memory, and
    use this history to generate responses. This can be useful to keep
    the conversation flowing naturally, and to keep the context of the
    conversation intact. While recommended, it's important to note that
    the data is stored in memory, non-encrypted, and will be lost when
    the application is restarted.
    """

    conversation_prompt = ("You will get a copy of the conversation history "
                           "with this user so far. Your previous messages "
                           "are prefixed with 'You: '. Do not include this "
                           "'You: ' in your actual replies. Respond according "
                           "to the users' last message, naturally as if conversing "
                           "with a human, taking the history in the dialogue "
                           "you've already had. \n\n")

    detect_memory_prompt = ("Determine if this message contains something the user "
                            "shares with you that you are expected to remember. It "
                            "could be anything from a name, a place, a date, a task, "
                            "or something they share about their life. It could be a "
                            "direct encouragement to remember something for the future, "
                            "or a clear directive to create a memory of something. It "
                            "could also just be a detail shared with you, that a human "
                            "would remember about them. If you think you should remember "
                            "something, Read the content of what to remember from the "
                            "user message and return the memory in this format: "
                            "'[MEMORY]: {your memory content here}'. If the message does "
                            "not match memory making or is a question, return 0")

    def __init__(self,
                 api_key: str,
                 model: str,
                 system_prompt: str = None,
                 max_tokens: int = None,
                 enable_conversations: bool = False,
                 enable_memories: bool = False,
                 max_conversation_length: int = 32_000,
                 allowed_intercepts: list[PyttmanPluginIntercept] = None):
        super().__init__(allowed_intercepts)
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt
        self.session = requests.Session()
        self.url = "https://api.openai.com/v1/chat/completions"
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.enable_conversations = enable_conversations
        self.max_conversation_length = max_conversation_length
        self.enable_memories = enable_memories
        self.rag_memories_path: Path | None = None
        self.long_term_memory: RagMemoryBank | None = None
        self.conversation_rag = {}

        self.session.headers.update({"Content-Type": "application/json"})
        self.session.headers.update({"Accept-Type": "application/json"})
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

        del self.api_key

    def on_app_start(self):
        if (static_files_dir := self.app.settings.STATIC_FILES_DIR) is None:
            static_files_dir = Path(self.app.settings.APP_BASE_DIR / "static")

        self.rag_memories_path = static_files_dir / "rag_memories" / "memories.json"
        self.long_term_memory = RagMemoryBank(self.rag_memories_path)

        pyttman.logger.log("- [OpenAIPlugin]: Plugin started.")
        if self.enable_memories:
            self.long_term_memory.load_memories()
        pyttman.logger.log("- [OpenAIPlugin]: Loaded")

    def _prepare_rag_prompt(self, message: MessageMixin) -> str:
        """
        Use RAG to prepend conversation history with this user to
        the outgoing llm request.
        """
        if not self.enable_conversations:
            return message.as_str()

        conversation = ""
        for user_message, ai_message in zip_longest(
            self.conversation_rag[message.author]["user"],
            self.conversation_rag[message.author]["ai"],
                fillvalue=""
        ):
            if user_message:
                conversation += f"User: {user_message}\n"
            if ai_message:
                conversation += f"You: {ai_message}\n"
        return conversation + f"User: {message.as_str()}\n"

    def _prepare_payload(self, message: MessageMixin) -> dict:
        """
        Prepare a payload towards OpenAI.
        """
        if self.enable_conversations:
            user_prompt = self._prepare_rag_prompt(message)
            system_prompt = self.system_prompt + self.conversation_prompt
            pyttman.logger.log(f" - [OpenAIPlugin]: conversation size "
                               f"for user {message.author}: {len(user_prompt)}")
        else:
            system_prompt = self.system_prompt
            user_prompt = message.as_str()

        if self.enable_memories:
            memories = self.long_term_memory.get_memories(message.author)
            system_prompt += (f"\nThese are your long term memories "
                              f"with this user: {"\n".join(memories)}")

        return OpenAiRequestPayload(
            model=self.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt).as_json()

    def before_router(self, message: MessageMixin):
        """
        Executes before the router resolves the message to an intent.
        """
        payload = self._prepare_payload(message)
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens

        try:
            response = self.session.post(self.url, json=payload)
            response_content = response.json()["choices"][0]["message"]["content"]
            message.content = response_content
            return message
        except requests.exceptions.RequestException as e:
            pyttman.logger.log(level="error",
                               message=f"OpenAIPlugin: Request to "
                                       f"OpenAI API failed: {e}")
            return Reply("I'm sorry, I couldn't generate a response for you.")

    def create_memory_if_applicable(self, message) -> str or None:
        """
        Create curated RAG memory prompts, stored to file locally
        """
        payload = OpenAiRequestPayload(
            model=self.model,
            system_prompt=self.detect_memory_prompt,
            user_prompt=message.as_str()).as_json()

        try:
            response = self.session.post(self.url, json=payload)
            memory = response.json()["choices"][0]["message"]["content"]
            if str(memory) == "0":
                return None
            return memory
        except requests.exceptions.RequestException as e:
            pyttman.logger.log(level="error",
                               message=f"OpenAIPlugin: Request to "
                                       f"OpenAI API failed: {e}")
            return None


    def no_intent_match(self, message: MessageMixin) -> Reply | None:
        """
        Hook. Executed when no intent matches the user's message.
        """
        if new_memory := self.create_memory_if_applicable(message):
            self.long_term_memory.append_memory(message.author, new_memory)
            self.long_term_memory.save()

        if self.conversation_rag.get(message.author) is None:
            self.conversation_rag[message.author] = {"user": [message.as_str()], "ai": []}
        else:
            self.conversation_rag[message.author]["user"].append(message.as_str())

        while True:
            user_length = len("".join(self.conversation_rag[message.author]["user"]))
            ai_length = len("".join(self.conversation_rag[message.author]["ai"]))

            if user_length + ai_length > self.max_conversation_length:
                self.conversation_rag[message.author]["user"].pop(0)
                self.conversation_rag[message.author]["ai"].pop(0)
            else:
                break

        error_response = Reply("I'm sorry, I couldn't generate a response for you.")
        payload = self._prepare_payload(message)

        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens

        try:
            response = self.session.post(self.url, json=payload)
        except requests.exceptions.RequestException as e:
            pyttman.logger.log(level="error",
                               message=f"OpenAIPlugin: Request to OpenAI API failed: {e}")
            return error_response

        if not response.ok:
            pyttman.logger.log(level="error",
                               message=f"OpenAIPlugin: Request to OpenAI "
                                       f"API failed: {response.text}")
            return error_response

        try:
            gpt_content = response.json()["choices"][0]["message"]["content"]
            self.conversation_rag[message.author]["ai"].append(gpt_content)
            if new_memory:
                gpt_content = f"Memory updated.\n{gpt_content}"
            return Reply(gpt_content)
        except KeyError:
            pyttman.logger.log(level="error",
                               message="OpenAIPlugin: No response from OpenAI API.")
            return error_response

