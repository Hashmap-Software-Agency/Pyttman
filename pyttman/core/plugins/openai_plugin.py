from functools import partial
from itertools import zip_longest

import requests

import pyttman
from pyttman.core.containers import MessageMixin, Reply
from pyttman.core.plugins.base import PyttmanPlugin, PyttmanPluginIntercept


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

    The plugin supports a conversational mode. When this is enabled, the
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

    def __init__(self,
                 api_key: str,
                 model: str,
                 system_prompt: str = None,
                 max_tokens: int = None,
                 enable_conversations: bool = False,
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
        self.message_cache = {}

        self.session.headers.update({"Content-Type": "application/json"})
        self.session.headers.update({"Accept-Type": "application/json"})
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        del self.api_key

    def _prepare_user_prompt(self, message: MessageMixin) -> str:
        if not self.enable_conversations:
            return message.as_str()

        conversation = ""
        for user_message, ai_message in zip_longest(
            self.message_cache[message.author]["user"],
            self.message_cache[message.author]["ai"],
                fillvalue=""
        ):
            if user_message:
                conversation += f"User: {user_message}\n"
            if ai_message:
                conversation += f"You: {ai_message}\n"

        return conversation + f"User: {message.as_str()}\n"

    def _prepare_payload(self, message: MessageMixin) -> dict:
        user_prompt = self._prepare_user_prompt(message)
        if self.enable_conversations:
            system_prompt = self.system_prompt + self.conversation_prompt
            pyttman.logger.log(f" - [OpenAIPlugin]: conversation size "
                               f"for user {message.author}: {len(user_prompt)}")
        else:
            system_prompt = self.system_prompt

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }
        return payload

    def before_router(self, message: MessageMixin):
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
                               message=f"OpenAIPlugin: Request to OpenAI API failed: {e}")
            return Reply("I'm sorry, I couldn't generate a response for you.")


    def no_intent_match(self, message: MessageMixin) -> Reply | None:
        """
        Hook. Executed when no intent matches the user's message.
        """
        if self.message_cache.get(message.author) is None:
            self.message_cache[message.author] = {"user": [message.as_str()], "ai": []}
        else:
            self.message_cache[message.author]["user"].append(message.as_str())

        while True:
            user_length = len("".join(self.message_cache[message.author]["user"]))
            ai_length = len("".join(self.message_cache[message.author]["ai"]))

            if user_length + ai_length > self.max_conversation_length:
                self.message_cache[message.author]["user"].pop(0)
                self.message_cache[message.author]["ai"].pop(0)
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
            self.message_cache[message.author]["ai"].append(gpt_content)
            return Reply(gpt_content)
        except KeyError:
            pyttman.logger.log(level="error",
                               message="OpenAIPlugin: No response from OpenAI API.")
            return error_response

