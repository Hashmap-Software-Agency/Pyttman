import os
from unittest import TestCase
from dotenv import load_dotenv
from pyttman.core.containers import Message, Reply
from pyttman.core.plugins.openai_plugin import OpenAIPlugin


class TestOpenAIPlugin(TestCase):

    def setUp(self):
        load_dotenv()

        self.plugin = OpenAIPlugin(
            api_key=os.environ["OPENAI_API_KEY"],
            system_prompt=os.environ["OPENAI_SYSTEM_PROMPT"],
            model="gpt-4o-mini",
            max_tokens=580)

    def test_no_intent_match(self):

        message = Message("What is the capital of France?")
        reply = self.plugin.no_intent_match(message)

        self.assertIsInstance(reply, Reply)
        self.assertTrue(reply.content)
