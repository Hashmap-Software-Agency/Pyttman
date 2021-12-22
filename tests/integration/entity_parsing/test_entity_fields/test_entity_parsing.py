
from pyttman.core.communication.models.containers import Message
from tests.integration.entity_parsing.base import _TestEntityParsingBaseCase
from tests.integration.entity_parsing.mockups import *


class TestEntityParserWithEmptyValueParserLowerCase_ShouldSucceed(
    _TestEntityParsingBaseCase):
    mock_intent_cls = TestableEntityParserWithIntAndStringField

    # Lowercase
    mock_message = Message("add expense some shopped item price 695,5684")

    def test_respond(self):
        self.parse_message_for_entities()
        item = self.get_entity_value("item").value
        price = self.get_entity_value("price").value
        self.assertEqual("some shopped item", item)
        self.assertEqual(695.5684, price)
        self.assertIsInstance(price, float)


class TestEntityFieldWithValidStrings(_TestEntityParsingBaseCase):
    mock_intent_cls = TestableEntityParserValidStrings

    # Lowercase
    mock_message = Message("add expense food price 695,5684")

    def test_respond(self):
        self.parse_message_for_entities()
        item = self.get_entity_value("item").value
        price = self.get_entity_value("price").value
        self.assertEqual("food", item)
        self.assertEqual(695.5684, price)
        self.assertIsInstance(price, float)


class TestEntityFieldWithInvalidStrings(_TestEntityParsingBaseCase):
    mock_intent_cls = TestableEntityParserValidStrings

    # Lowercase
    mock_message = Message("add expense something else price 695,5684")

    def test_respond(self):
        self.parse_message_for_entities()
        item = self.get_entity_value("item").value
        price = self.get_entity_value("price").value
        self.assertIsNone(item)
        self.assertEqual(695.5684, price)
        self.assertIsInstance(price, float)
