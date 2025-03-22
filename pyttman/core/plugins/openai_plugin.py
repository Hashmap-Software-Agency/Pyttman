import tiktoken
import json
from dataclasses import dataclass, field
from datetime import datetime
from itertools import zip_longest
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

import requests

import pyttman
from pyttman.core.containers import MessageMixin, Reply
from pyttman.core.plugins.base import PyttmanPlugin, PyttmanPluginIntercept


@dataclass
class OpenAiRequestPayload:
    model: str
    system_prompt: str
    user_prompt: str
    max_tokens: int = None

    def as_json(self):
        output = {
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
        if self.max_tokens:
            output["max_tokens"] = self.max_tokens
        return output

@dataclass
class RagMemoryBank:
    """
    The OpenAiRagMemoryBank is a dataclass that holds
    the conversation history with a user, and the
    memories that the AI should remember.

    Saving the RAG data can be defined by the user, building the app.
    They can provide callbacks for us to use when CRUD:ing memories.
    """
    file_path: Path | None = None
    memories: dict[str, list[str]] = field(default_factory=dict)
    callbacks: dict[str, Callable or None] = field(default_factory=dict)

    def __post_init__(self):
        self.callbacks = {
            "purge_all_memories": None,
            "purge_memories": None,
            "append_memory": None,
            "get_memories": None,
        }

    def _execute_callback(self, callback_name: str, *args) -> any:
        """
        Execute a callback if it's defined.
        """
        try:
            if (callback := self.callbacks.get(callback_name)) is not None:
                response = callback(*args)
                return True if response is None else response
        except Exception as e:
            pyttman.logger.log(level="error",
                               message=f"OpenAIPlugin: RagMemoryBank: "
                                       f"callback {callback_name} failed: {e}")

    def _load_memories_from_file(self):
        """
        Load the memories source
        """
        if self.file_path is None:
            raise ValueError("OpenAIPlugin: RagMemoryBank: Using file storage "
                             "fallback failed. No file path defined for the "
                             "memory bank.")

        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.save_to_file()

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
            self.memories = data["memories"]

    def _get_memory_from_file(self, key):
        """
        Fallback, unless user implements callback. Use file-based memories.
        """
        if not self.memories:
            self._load_memories_from_file()
        return self.memories.get(str(key), [])

    def _add_memory_to_file(self, key, memory):
        if not self.memories:
            self._load_memories_from_file()

        key = str(key)
        if self.memories.get(key) is None:
            self.memories[key] = [memory]
        else:
            self.memories[key].append(memory)
        self.save_to_file()

    def purge_all_memories(self):
        """
        Purge all memories.
        """
        if self._execute_callback("purge_all_memories") is not None:
            return
        self.memories.clear()

    def purge_memories(self, key: str):
        """
        Purge all memories for a given key.
        """
        if self._execute_callback("purge_memories", key) is not None:
            return
        self.memories[key] = []

    def get_memories(self, key: str) -> tuple[str] or list[str]:
        """
        Return the memories for a given key.
        """
        if (memories := self._execute_callback("get_memories", key)) is not None:
            if not isinstance(memories, (list, tuple)):
                raise ValueError("OpenAIPlugin: The memories callback must "
                                 "return a list or tuple.")
            return memories
        return self._get_memory_from_file(key)

    def add_memory(self, key: str, memory: str):
        """
        Append a memory to the memory bank.
        """
        if callback_return := self._execute_callback("add_memory", key, memory):
            return callback_return
        self._add_memory_to_file(key, memory)

    def save_to_file(self):
        """
        Save the memories to a file.
        """
        with open(self.file_path, "w", encoding="utf-8") as f:
            data = self.as_json()
            f.write(json.dumps(data, indent=4))

    def as_json(self):
        return {"memories": self.memories}

    def memories_as_str(self, key: str) -> str:
        """
        Return the memories as a string.
        """
        key = str(key)
        base = "These are your long term memories with this user: "
        memories = self.get_memories(key)
        return base + "\n".join(memories)


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

    :param api_key: The OpenAI API key to use for the plugin.
    :param model: The model to use for the OpenAI API. For valid options,
        see OpenAI's API documentation.
    :param system_prompt: A system prompt to use for the OpenAI API. Set
        this to configure your app behavior.
    :param max_tokens: The maximum number of tokens to use for the OpenAI API.
    :param enable_conversations: Enable RAG: conversational mode. This will
        keep a conversation history for each user,
        greatly improving the experience for conversational applications.
        Disable for stateless apps.
    :param enable_memories: Enable memory making. This will allow the AI to
        remember details about the user, automatically.
        To define custom functions for CRUD operations with memory to use
        a database or other source, provide the callbacks for the plugin to use.
    :param max_conversation_length: The maximum length of the conversation
        history to keep in memory. When the conversation history exceeds this
        length, the memory is truncated oldest first, making for a seamless
        experience.
    :param allowed_intercepts: A list of PyttmanPluginIntercept enums that
        define when the plugin should be executed in the Pyttman application.
        Use these intercepts to align the system prompts you set, with
        the time of execution in the Pyttman application. For example,
        use PyttmanPluginIntercept.before_router to correct spelling mistakes
        or otherwise pre-process the message before it's sent on to the intents.
        In this case, the system prompt could be a spell-checker prompt,
        return the message to the user spell corrected and otherwise intact.
        Stack multiple plugins with different intercept points to create
        a powerful AI system.
    :param time_aware: Set to True if the plugin should be aware of the current
        datetime. If True, the system prompt will be prepended with the current
        datetime, making the AI aware of the time of day. This can really
        improve the experience since the AI can reason about when things
        occur, and you can introduce reasoning about future and past events
        with the AI.
    :param time_zone: The timezone to use for the time awareness. If not set,
        the system will use the system timezone.
    """
    model_context_limits = {
        "gpt-4o": 128_000,
        "gpt-4o-mini": 128_000,
        "gpt-4-turbo": 128_000,
        "gpt-4": 8_192,
        "gpt-4-32k": 32_768,
        "gpt-3.5-turbo": 4_096,
        "gpt-3.5-turbo-16k": 16_000
    }

    conversation_prompt = ("\nYou will get a copy of the conversation history "
                           "with this user so far. Your previous messages "
                           "are prefixed with 'You: '. Do not include this "
                           "'You: ' in your actual replies. Respond according "
                           "to the users' last message, naturally as if conversing "
                           "with a human, taking the history in the dialogue "
                           "you've already had.\n")

    detect_memory_prompt = ("\nDetermine if the last message with the user contains "
                            "something the user shares with you that you are expected "
                            "to remember. It could be anything from a name, a place, "
                            "a date, a task, or something they share about their life. "
                            "It could be a direct encouragement to remember something "
                            "for the future, or a clear directive to create a memory of "
                            "something. It could also just be a detail shared with you, "
                            "that a human would remember about them. If you think you "
                            "should remember something, Read the content of what to "
                            "remember from the user message and return the memory in "
                            "the highest possible detail  in this format: '[MEMORY]: "
                            "{your memory content here}'. If the message does not match "
                            "memory making or is a question, return 0.\n")

    def __init__(self,
                 api_key: str,
                 model: str,
                 system_prompt: str = None,
                 max_response_length: int = None,
                 enable_conversations: bool = False,
                 enable_memories: bool = False,
                 memory_updated_notice: str = None,
                 allowed_intercepts: list[PyttmanPluginIntercept] = None,
                 time_aware: bool = False,
                 time_zone: ZoneInfo = None,
                 purge_all_memories_callback: callable or None = None,
                 purge_memories_callback: callable or None = None,
                 add_memory_callback: callable or None = None,
                 get_memories_callback: callable or None = None):

        if time_zone and not isinstance(time_zone, ZoneInfo):
            raise ValueError("OpenAIPlugin: time_zone must be a ZoneInfo object,"
                             " or None to use the system timezone.")
        super().__init__(allowed_intercepts)

        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt
        self.session = requests.Session()
        self.url = "https://api.openai.com/v1/chat/completions"
        self.api_key = api_key
        self.enable_conversations = enable_conversations
        self.enable_memories = enable_memories
        self.rag_memories_path: Path | None = None
        self.long_term_memory: RagMemoryBank | None = None
        self.time_aware = time_aware
        self.zone_info = time_zone
        self.conversation_rag = {}
        self.memory_updated_notice = memory_updated_notice or "Memory updated."

        self._purge_all_memories_callback = purge_all_memories_callback
        self._purge_memories_callback = purge_memories_callback
        self._add_memory_callback = add_memory_callback
        self._get_memories_callback = get_memories_callback

        self.session.headers.update({"Content-Type": "application/json"})
        self.session.headers.update({"Accept-Type": "application/json"})
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

        if max_response_length is not None:
            example_token = "b" * int(max_response_length * 0.8)
            self.max_response_tokens = self._convert_to_tokens(example_token)
        else:
            self.max_response_tokens = None
        del self.api_key

    def _convert_to_tokens(self, text):
        """
        Convert text to tokens for the model.
        """
        encoding = tiktoken.encoding_for_model(self.model)
        return len(encoding.encode(text))

    def tokens_exceeded(self, text):
        """
        Determine if the amount of tokens for the system prompt +
        user prompt + output tokens exceeds the limit for the model.
        """
        text_tokens = self._convert_to_tokens(text)
        model_context = self.model_context_limits.get(self.model)
        response_token_limit = self.max_response_tokens or 0
        return text_tokens + response_token_limit > model_context

    def on_app_start(self):
        if (static_files_dir := self.app.settings.STATIC_FILES_DIR) is None:
            static_files_dir = Path(self.app.settings.APP_BASE_DIR / "static")
        self.rag_memories_path = static_files_dir / "rag_memories" / "memories.json"
        self.long_term_memory = RagMemoryBank(self.rag_memories_path)

        self.long_term_memory.callbacks["purge_all_memories"] = self._purge_all_memories_callback
        self.long_term_memory.callbacks["purge_memories"] = self._purge_memories_callback
        self.long_term_memory.callbacks["add_memory"] = self._add_memory_callback
        self.long_term_memory.callbacks["get_memories"] = self._get_memories_callback

        pyttman.logger.log("- [OpenAIPlugin]: Plugin started.")

    def conversational_context_prompt(self,
                                      message: MessageMixin,
                                      system_prompt: str) -> str:
        """
        Use RAG to prepend conversation history with this user to
        the outgoing llm request.
        """
        user_prompt = message.as_str()
        if not self.enable_conversations:
            return user_prompt

        try:
            user_messages = self.conversation_rag[message.author.id]["user"]
            ai_messages = self.conversation_rag[message.author.id]["ai"]
        except KeyError:
            return user_prompt

        conversation = ""
        for user_message, ai_message in zip_longest(user_messages,
                                                    ai_messages,
                                                    fillvalue=""):

            if self.tokens_exceeded(system_prompt + conversation):
                pyttman.logger.log("- [OpenAIPlugin]: Could not include "
                                   "the full conversation history in the "
                                   f"system prompt. for user {message.author.id}. "
                                   f"The conversation history exceeds the token limit "
                                   f"for the model. Some context will be lost in "
                                   f"this request.")
                break
            if user_message:
                conversation += f"User: {user_message}\n"
            if ai_message:
                conversation += f"You: {ai_message}\n"
        return conversation + f"User: {message.as_str()}\n"

    def prepare_payload(self, message: MessageMixin) -> OpenAiRequestPayload:
        """
        Prepare a payload towards OpenAI.
        """
        system_prompt = self.system_prompt
        if self.enable_memories:
            memory_prompt = ("\nThese are your long term memories with "
                             "this user: {}. Compare the date with the "
                             "largest date in the conversation, to evaluate how "
                             "long ago the memory was created and use "
                             "this information when generating a response.\n")

            memories = self.long_term_memory.get_memories(message.author.id)
            if self.tokens_exceeded(memory_prompt.format("\n".join(memories))):
                pyttman.logger.log(level="warning",
                                   message=f" - [OpenAIPlugin]: Tokens exceeded - too "
                                           f"many memories for user {message.author.id}. "
                                           f"Consider purging memories. Some "
                                           f"context will be lost in this request.")

            while self.tokens_exceeded("\n".join(memories)):
                memories = memories[1:]

            memory_prompt = memory_prompt.format("\n".join(memories))
            system_prompt = f"{system_prompt}\n{memory_prompt}"

        if self.enable_conversations:
            system_prompt = system_prompt + self.conversation_prompt
            user_prompt = self.conversational_context_prompt(message, system_prompt)
            pyttman.logger.log(f" - [OpenAIPlugin]: conversation size "
                               f"for user {message.author.id}: {len(user_prompt)}")
        else:
            system_prompt = self.system_prompt
            user_prompt = message.as_str()

        if self.time_aware:
            now = datetime.now(tz=self.zone_info) if self.zone_info else datetime.now()
            system_prompt = (f"\n{system_prompt}\nThe date and time right now is: "
                             f"{now.strftime('%Y-%m-%d %H:%M:%S')}. Override any previous "
                             f"smaller date time in the conversation history with this "
                             f"date and time.")

        total_input_tokens = self._convert_to_tokens(user_prompt + system_prompt)
        if total_input_tokens > self.model_context_limits[self.model]:
            pyttman.logger.log(level="warning",
                               message=f" - [OpenAIPlugin]: The input tokens exceed the "
                                       f"model context limit for the model {self.model}. "
                                       f"Consider reducing the input size. "
                                       f"Total input tokens: {total_input_tokens}. "
                                       f"Model context limit: "
                                       f"{self.model_context_limits[self.model]}")
        else:
            pyttman.logger.log(f" - [OpenAIPlugin]: total input tokens for user "
                               f"{message.author.id}: {total_input_tokens}")

        payload = OpenAiRequestPayload(
            model=self.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt)
        return payload

    def before_router(self, message: MessageMixin):
        """
        Executes before the router resolves the message to an intent.
        """
        payload = self.prepare_payload(message)
        if self.max_response_tokens:
            payload["max_tokens"] = self.max_response_tokens

        response_json = None
        try:
            response = self.session.post(self.url, json=payload.as_json())
            response_json = response.json()
            response_content = response_json["choices"][0]["message"]["content"]
            message.content = response_content
            return message
        except (requests.exceptions.RequestException, KeyError) as e:
            pyttman.logger.log(level="error",
                               message=f"OpenAIPlugin: Request to "
                                       f"OpenAI API failed: {e}")
            pyttman.logger.log("Response content for failing response:", response_json)
            return Reply("I'm sorry, I couldn't generate a response for you.")

    def create_memory_if_applicable(self, message, user_prompt) -> str or None:
        """
        Create a memory if the message is a memory making message.
        If time awareness is enabled, the memory will be prepended
        with the current date and time in the user-defined timezone
        or the system timezone as fallback.
        """
        if self.enable_conversations:
            conversation_context = self.conversational_context_prompt(message, user_prompt)
            detect_memory_prompt = f"{conversation_context} {self.detect_memory_prompt}"
        else:
            detect_memory_prompt = self.detect_memory_prompt

        payload = OpenAiRequestPayload(
            model=self.model,
            system_prompt=detect_memory_prompt,
            user_prompt=message.as_str()).as_json()

        try:
            response = self.session.post(self.url, json=payload)
            memory = response.json()["choices"][0]["message"]["content"]
            if str(memory) == "0":
                return None
            if not self.time_aware:
                return memory

            if self.zone_info:
                now = datetime.now(tz=self.zone_info)
            else:
                now = datetime.now()
            temporal_addition = f"You memorized this {now.strftime('%Y-%m-%d %H:%M:%S')}."
            return f"{memory} - {temporal_addition}"
        except requests.exceptions.RequestException as e:
            pyttman.logger.log(level="error",
                               message=f"OpenAIPlugin: Request to "
                                       f"OpenAI API failed: {e}")
            return None


    def no_intent_match(self, message: MessageMixin) -> Reply | None:
        """
        Hook. Executed when no intent matches the user's message.
        """

        if self.conversation_rag.get(message.author.id) is None:
            self.conversation_rag[message.author.id] = {"user": [message.as_str()], "ai": []}
        else:
            self.conversation_rag[message.author.id]["user"].append(message.as_str())

        error_response = Reply("I'm sorry, I couldn't generate a response for you.")
        payload = self.prepare_payload(message)
        if new_memory := self.create_memory_if_applicable(message, payload.user_prompt):
            self.long_term_memory.add_memory(message.author.id, new_memory)

        if self.max_response_tokens:
            payload.max_tokens = self.max_response_tokens
            print("Max response tokens:", payload.max_tokens)

        try:
            response = self.session.post(self.url, json=payload.as_json())
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
            self.conversation_rag[message.author.id]["ai"].append(gpt_content)
            if new_memory:
                gpt_content = f"{self.memory_updated_notice}\n{gpt_content}"
            return Reply(gpt_content)
        except KeyError:
            pyttman.logger.log(level="error",
                               message="OpenAIPlugin: No response from OpenAI API.")
            return error_response
