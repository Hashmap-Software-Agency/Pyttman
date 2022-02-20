from abc import ABC
from typing import Type, Any
from unittest import TestCase

from pyttman.core.communication.models.containers import Message, ReplyStream, \
    Reply
from pyttman.core.intent import Intent


class ImplementedTestIntent(Intent):
    """
    This class is used during testing to simulate the
    user defined Intent classes in a Pyttman application.

    Implemented unit tests for asserting the EntityParser API or
    MessageRouter classes, Storage, or any of the other building
    blocks in the Pyttman Framework should overload this class
    with the intent to be tested.
    """
    def respond(self, message: Message) -> Reply | ReplyStream:
        return Reply(f"'{self.__class__.__name__}' matched a message")


class PyttmanInternalTestCase(TestCase):
    """
    Base class for a test case testing EntityParser configurations
    """
    mock_intent_cls: Type[Intent]
    mock_message: Message
    expected_entities: dict[str: str] = {}

    class IntentClass(Intent, ABC):
        """
        Test cases overload this inner class
        """
        pass

    def setUp(self) -> None:
        self.mock_intent = self.IntentClass()
        self.intent_reply = None

        # Show the test explanation in the log output
        print(f"'{self.__class__.__name__}':\n"
              f'\t\t"""{self.IntentClass.__doc__}"""',
              end="\n\n")

    def get_entity_value(self, entity_name):
        try:
            return self.mock_message.entities[entity_name]
        except KeyError:
            raise RuntimeError(f"Warning! No field named '{entity_name}' was "
                               f"found in the EntityParser class in this test "
                               f"suite")

    def test_entity_parser_entity_values(self):
        """
        Asserts that the implementation EntityParser in subclasses of
        this base class behaves as expected, by comparing the values
        parsed by the EntityParser to a set of expected values.
        :return:
        """
        if not self.expected_entities:
            print("\t\t(!) Warning: 'expected_entities' dict is empty; "
                  "skipping EntityParser assertion for this test suite.")
            return

        print("\t\tChecking EntityParser...")
        self.parse_message_for_entities()

        for field_name, expected_value in self.expected_entities.items():
            value = self.get_entity_value(field_name)
            self.assertEqual(value,
                             expected_value,
                             f"\t\tEntityParser test FAILED.\n"
                             f"\t\tThe entity '{field_name}' did not contain "
                             f"the expected value '{expected_value}' "
                             f"but rather: '{value}'\n\n")

        print("\t\tEntityParser test PASSED")

    def parse_message_for_entities(self):
        # Truncate 'lead' and 'trail' from the message before parsing
        self.intent_reply = self.mock_intent.process(self.mock_message)
        print(f"\t\tResult: {self.mock_message.entities}")
