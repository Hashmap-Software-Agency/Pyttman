
from typing import Type
from unittest import TestCase

from ordered_set import OrderedSet

from pyttman.core.communication.models.containers import Message
from pyttman.core.intent import Intent
from tests.integration.entity_parsing.mockups import \
    TestableEntityParserUsingOnlyPreAndSuffixes, \
    TestableEntityParserIntentUsingIdentifier, \
    TestableEntityParserIntentUsingIdentifierAndPrefixesSuffixes, \
    TestableEntityParserIntentUsingIdentifierAndPrefixesSuffixes_CapitalizedChoices, \
    TestableEntityParserIdentifiersAndSuffixes_FoodMessage_ShouldSucceed, \
    TestableEntityParserIdentifiersAndSuffixes_AdvertisementMessage_ShouldSucceed, \
    TestableEntityParserShouldIgnoreLeadAndTrailInEntities, \
    TestableEntityParserWithTwoValueParsers


# Unit tests


class _TestBaseCase(TestCase):
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


class TestEntityParserWithEmptyValueParserCapitalized_ShouldSucceed(_TestBaseCase):
    mock_intent_cls = TestableEntityParserWithTwoValueParsers

    # Capitalized
    mock_message = Message("Add expense some shopped item 695")

    def test_respond(self):
        self.parse_message_for_entities()
        self.assertEqual("some shopped item", self.get_entity_value("item"))
        self.assertEqual("695", self.get_entity_value("price"))


class TestEntityParserWithEmptyValueParserLowerCase_ShouldSucceed(_TestBaseCase):
    mock_intent_cls = TestableEntityParserWithTwoValueParsers

    # Lowercase
    mock_message = Message("add expense some shopped item 695")

    def test_respond(self):
        self.parse_message_for_entities()
        self.assertEqual("some shopped item", self.get_entity_value("item"))
        self.assertEqual("695", self.get_entity_value("price"))


class TestEntityParserPrefixesAndSuffixes_ShouldSucceed(_TestBaseCase):
    mock_intent_cls = TestableEntityParserUsingOnlyPreAndSuffixes
    mock_message = Message("man in the mirror with Michael Jackson on spotify")

    def test_respond(self):
        self.parse_message_for_entities()
        self.assertEqual("man in the mirror", self.get_entity_value("song"))
        self.assertEqual("spotify", self.get_entity_value("platform"))


class TestEntityParserIdentifiers_ShouldSucceed(_TestBaseCase):
    mock_intent_cls = TestableEntityParserIntentUsingIdentifier
    mock_message = Message("create a new contact Will "
                           "Byers on mobile with 0805552859 "
                           "and do it on 2021-09-20-10:40")

    def test_respond(self):
        self.parse_message_for_entities()

        self.assertEqual("Will Byers", self.get_entity_value("contact"))
        self.assertEqual("0805552859", self.get_entity_value("phone_number"))
        self.assertEqual("mobile", self.get_entity_value("phone_standard"))
        self.assertEqual("2021-09-20-10:40", self.get_entity_value("date_change"))


class TestEntityParserIdentifiersPrefixesSuffiixes_ShouldFail(_TestBaseCase):
    mock_intent_cls = TestableEntityParserIntentUsingIdentifierAndPrefixesSuffixes
    mock_message = Message("create a new contact Will "
                           "Byers on mobile with 0805552859 "
                           "and do it on 2021-09-20-10:40")

    def test_respond(self):
        self.parse_message_for_entities()

        self.assertIsNone(self.get_entity_value("contact"))
        self.assertIsNone(self.get_entity_value("number"))
        self.assertIsNone(self.get_entity_value("date"))


class TestEntityParserIdentifiersPrefixesSuffiixes_ShouldSucceed(_TestBaseCase):
    mock_intent_cls = TestableEntityParserIntentUsingIdentifierAndPrefixesSuffixes
    mock_message = Message("create a new contact name Will "
                           "Byers on mobile with number: 0805552859 "
                           "and do it at 2021-09-20-10:40")

    def test_respond(self):
        self.parse_message_for_entities()

        self.assertEqual("Will Byers", self.get_entity_value("contact"))
        self.assertEqual("0805552859", self.get_entity_value("phone_number"))
        self.assertEqual("mobile", self.get_entity_value("phone_standard"))
        self.assertEqual("2021-09-20-10:40", self.get_entity_value("date_change"))


class TestEntityParserChoiceParserWithCaseMixedChoices_ShouldSucceed(_TestBaseCase):
    mock_intent_cls = TestableEntityParserIntentUsingIdentifierAndPrefixesSuffixes_CapitalizedChoices
    mock_message = Message("I love the colors of october")

    def test_respond(self):
        self.parse_message_for_entities()
        self.assertEqual("October", self.get_entity_value("month"))


class TestEntityParserChoiceParser_Capitalized_ShouldSucceed(_TestBaseCase):
    mock_intent_cls = TestableEntityParserIntentUsingIdentifierAndPrefixesSuffixes_CapitalizedChoices
    mock_message = Message("I love the colors of October")

    def test_respond(self):
        self.parse_message_for_entities()
        self.assertEqual("October", self.get_entity_value("month"))


class TestEntityParserIDentifierPrefixesSuffixesMultipleChoices_1_ShouldSucceed(_TestBaseCase):
    mock_intent_cls = TestableEntityParserIdentifiersAndSuffixes_FoodMessage_ShouldSucceed
    mock_message = Message("search for vegetarian recipes on all websites "
                           "max ingredients 10 and 4 servings on RestaurantName")

    def test_respond(self):
        self.parse_message_for_entities()

        self.assertEqual("vegetarian", self.get_entity_value("preference"))
        self.assertEqual("10", self.get_entity_value("max_ingredients"))
        self.assertEqual("4", self.get_entity_value("servings"))
        self.assertEqual("RestaurantName", self.get_entity_value("restaurant"))


class TestEntityParserIDentifierPrefixesSuffixesMultipleChoices_3_ShouldSucceed(_TestBaseCase):
    mock_intent_cls = TestableEntityParserIdentifiersAndSuffixes_AdvertisementMessage_ShouldSucceed
    mock_message = Message("Search for ManufacturerA ManufacturerB Model123 "
                           "on page_a and page_b price 45000 60 results")

    def test_respond(self):
        self.parse_message_for_entities()

        self.assertEqual("ManufacturerA ManufacturerB", self.get_entity_value("manufacturer"))
        self.assertEqual("Model123", self.get_entity_value("model"))
        self.assertEqual(OrderedSet(['page_b', 'page_a']), self.get_entity_value("pages"))
        self.assertEqual("60", self.get_entity_value("maximum_results"))
        self.assertEqual("45000", self.get_entity_value("minimum_price"))


class EntityParserShouldIgnoreLeadAndTrailInEntities_ShouldSucceed(_TestBaseCase):
    mock_intent_cls = TestableEntityParserShouldIgnoreLeadAndTrailInEntities
    mock_message = Message("new app name")

    def test_respond(self):
        self.parse_message_for_entities()
        self.assertEqual("name", self.get_entity_value("name"))
