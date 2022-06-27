from abc import ABC
from typing import Type

from pyttman.core.ability import Ability
from pyttman.core.containers import Message, ReplyStream, \
    Reply
from pyttman.core.middleware.routing import FirstMatchingRouter
from pyttman.core.intent import Intent
from tests.module_helper import PyttmanInternalBaseTestCase


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


class PyttmanInternalTestBaseCase(PyttmanInternalBaseTestCase):
    """
    Base class for a test case testing EntityParser configurations
    """
    process_message = False
    test_intent_matching = False
    ability_cls = Ability
    intent_class = None
    mock_intent_cls: Type[Intent]
    mock_message: Message
    expected_entities: dict[str: str] = {}
    expected_reply: Reply | None = None

    class IntentClass(Intent, ABC):
        pass

    def setUp(self) -> None:
        if self.intent_class is not None:
            self.IntentClass = self.intent_class
        self.mock_intent = self.IntentClass()
        self.intent_reply: Reply | None = None
        self.main_ability = self.ability_cls(intents=(self.IntentClass,))
        self.router = FirstMatchingRouter(abilities=[self.main_ability],
                                          help_keyword="",
                                          intent_unknown_responses=["unknown"])

    def get_entity_value(self, entity_name):
        try:
            return self.mock_message.entities[entity_name]
        except KeyError:
            raise RuntimeError(f"Warning! No field named '{entity_name}' was "
                               f"found in this test suite")

    def test_entity_parser_entity_values(self):
        """
        Asserts that the implementation EntityParser in subclasses of
        this base class behaves as expected, by comparing the values
        parsed by the EntityParser to a set of expected values.
        :return:
        """
        if self.process_message is False:
            self.skipTest(
                f"EntityParser API test is disabled for "
                f"'{self.__class__.__name__}' -- Skipping ")

        # Show the test explanation in the log output
        print(f"\n'{self.__class__.__name__}':\n"
              f'\t"""{self.IntentClass.__doc__}"""',
              end="\n\n")

        print("\t\tChecking EntityParser...")
        self.parse_message_for_entities()
        print(f"\t\tIntent reply: {self.intent_reply}")

        for field_name, expected_value in self.expected_entities.items():
            value = self.get_entity_value(field_name)
            self.assertEqual(expected_value,
                             value,
                             f"\t\tEntityParser test FAILED.\n"
                             f"\t\tThe entity '{field_name}' did not contain "
                             f"the expected value '{expected_value}' "
                             f"but rather: '{value}'\n\n")

        print("\t\tEntityParser test PASSED")

    def parse_message_for_entities(self):
        # Truncate 'lead' and 'trail' from the message before parsing
        self.mock_intent.storage = self.main_ability.storage
        self.before_message_processing()
        self.intent_reply = self.router.process(self.mock_message,
                                                self.mock_intent,
                                                keep_alive_on_exc=False)
        print(f"\t\tResult: {self.mock_message.entities}")

        if self.expected_reply:
            self.assertEqual(self.intent_reply.as_str(),
                             self.expected_reply.as_str())
        self.after_message_processing()

    def test_intent_message_matching(self):
        """
        Tests that the Intent class matches a given message, as expected.
        """
        self.before_intent_matching()
        if self.test_intent_matching is False:
            self.skipTest(
                f"Intent matching test is disabled for "
                f"'{self.__class__.__name__}' -- Skipping ")

        expected_matching_intent = self.mock_intent
        matching_intents = self.router.get_matching_intent(self
                                                           .mock_message)

        self.assertNotEqual(len(matching_intents), 0,
                            msg=f"\n'{self.mock_intent}' didn't "
                                f"match '{self.mock_message.content}'")

        first_matching = matching_intents.pop()

        self.assertIs(expected_matching_intent.__class__,
                      first_matching.__class__)
        self.after_intent_matching()

    def after_message_processing(self):
        pass

    def after_intent_matching(self):
        pass

    def before_message_processing(self):
        pass

    def before_intent_matching(self):
        pass
