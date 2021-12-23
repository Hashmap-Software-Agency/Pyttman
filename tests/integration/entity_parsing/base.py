
from typing import Type
from unittest import TestCase

from pyttman.core.communication.models.containers import Message
from pyttman.core.intent import Intent


class _TestEntityParsingBaseCase(TestCase):
    """
    Base class for a test case testing EntityParser configurations
    """
    mock_intent_cls: Type[Intent]
    mock_message: Message

    def setUp(self) -> None:
        self.mock_intent = self.mock_intent_cls()
        self.intent_reply = None

    def get_entity_value(self, entity_name):
        return self.mock_message.entities.get(entity_name)

    def parse_message_for_entities(self):
        # Truncate 'lead' and 'trail' from the message before parsing
        self.intent_reply = self.mock_intent.process(self.mock_message)
        print(f"{self.__class__.__name__} ENTITIES:",
              self.mock_message.entities)
