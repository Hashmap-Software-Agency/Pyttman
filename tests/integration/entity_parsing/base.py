from abc import ABC
from typing import Type, Any
from unittest import TestCase, skip

from pyttman.core.ability import Ability
from pyttman.core.entity_parsing.routing import FirstMatchingRouter
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


class PyttmanInternalTestBaseCase(TestCase):
    """
    Base class for a test case testing EntityParser configurations
    """
    mock_intent_cls: Type[Intent]
    mock_message: Message
    expected_entities: dict[str: str] = {}

    class IntentClass(Intent, ABC):
        pass

    def setUp(self) -> None:
        self.mock_intent = self.IntentClass()
        self.intent_reply = None
        self.main_ability = Ability(intents=(self.IntentClass,))
        self.router = FirstMatchingRouter(abilities=[self.main_ability],
                                          help_keyword="",
                                          intent_unknown_responses=["unknown"])

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
            return

        # Show the test explanation in the log output
        print(f"\n'{self.__class__.__name__}':\n"
              f'\t\t"""{self.IntentClass.__doc__}"""',
              end="\n\n")

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

    def test_intent_message_matching(self):
        """
        Tests that the Intent class matches a given message, as expected.
        """
        if len(self.mock_intent.lead):
            expected_matching_intent = self.mock_intent
            matching_intent = self.router.get_matching_intent(
                self.mock_message).pop()
            self.assertIs(expected_matching_intent.__class__,
                          matching_intent.__class__)
