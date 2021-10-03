#     MIT License
#
#      Copyright (c) 2021-present Simon Olofsson
#
#      Permission is hereby granted, free of charge, to any person obtaining a copy
#      of this software and associated documentation files (the "Software"), to deal
#      in the Software without restriction, including without limitation the rights
#      to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#      copies of the Software, and to permit persons to whom the Software is
#      furnished to do so, subject to the following conditions:
#
#      The above copyright notice and this permission notice shall be included in all
#      copies or substantial portions of the Software.
#
#      THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#      IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#      FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#      AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#      LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#      OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#      SOFTWARE.
import unittest
from typing import Union, Type
from unittest import TestCase

from ordered_set import OrderedSet

from pyttman.core.communication.models.containers import Message, MessageMixin, Reply, ReplyStream
from pyttman.core.intent import Intent
from pyttman.core.parsing.identifiers import CapitalizedIdentifier, CellPhoneNumberIdentifier, DateTimeStringIdentifier, \
    IntegerIdentifier
from pyttman.core.parsing.parsers import ValueParser, ChoiceParser


class _TestableEntityParserConfiguredIntent(Intent):
    """
    Base class for entity parsing tests.
    """

    def respond(self, message: MessageMixin) -> Union[Reply, ReplyStream]:
        return Reply(self.entities)


class EntityParserWithEmptyValueParser(_TestableEntityParserConfiguredIntent):
    """
    Tests the use of a single ValueParser without any configuration """

    class EntityParser:
        item = ValueParser()


class TestEntityParserWithTwoValueParsers(_TestableEntityParserConfiguredIntent):
    """
    Tests the use of a single ValueParser without any configuration """

    class EntityParser:
        item = ValueParser(span=5)
        price = ValueParser(identifier=IntegerIdentifier)


class TestableEntityParserUsingOnlyPreAndSuffixes(_TestableEntityParserConfiguredIntent):
    """
    Intent class for testing Intent matching
    and Entity Parsing, specifically without
    identifiers but only using pre / suffixes.
    """

    class EntityParser:
        exclude = ("on",)
        song = ValueParser(span=10)
        artist = ValueParser(prefixes=("by", "with"), span=10)
        platform = ChoiceParser(choices=("spotify", "soundcloud"))


class TestableEntityParserIntentUsingIdentifier(_TestableEntityParserConfiguredIntent):
    """
    Intent class for testing Intent matching and Entity
    parsing, using identifiers, not pre/suffixes.
    """

    class EntityParser:
        contact = ValueParser(identifier=CapitalizedIdentifier, span=2)
        phone_number = ValueParser(identifier=CellPhoneNumberIdentifier)
        date_change = ValueParser(identifier=DateTimeStringIdentifier)
        phone_standard = ChoiceParser(choices=("mobile", "cell", "land", "landline"))


class TestableEntityParserIntentUsingIdentifierAndPrefixesSuffixes(_TestableEntityParserConfiguredIntent):
    """
    Intent class for testing Intent matching and Entity
    parsing, using identifiers AND pre/suffixes.
    """

    class EntityParser:
        contact = ValueParser(prefixes=("name",), identifier=CapitalizedIdentifier, span=2)
        phone_number = ValueParser(prefixes=("number",), identifier=CellPhoneNumberIdentifier)
        date_change = ValueParser(prefixes=("at",), identifier=DateTimeStringIdentifier)
        phone_standard = ChoiceParser(choices=("mobile", "cell", "land", "landline"))


class TestableEntityParserIdentifiersAndSuffixes_FoodMessage_ShouldSucceed(_TestableEntityParserConfiguredIntent):
    class EntityParser:

        restaurant = ValueParser(identifier=CapitalizedIdentifier, span=5)
        preference = ChoiceParser(choices=("vegetarian", "meatarian"))
        max_ingredients = ValueParser(prefixes=("ingredients",), identifier=IntegerIdentifier)
        servings = ValueParser(suffixes=("servings",), identifier=IntegerIdentifier)


class TestableEntityParserIdentifiersAndSuffixes_AdvertisementMessage_ShouldSucceed(_TestableEntityParserConfiguredIntent):

    class EntityParser:
        exclude = ("search", "for", "on")
        manufacturer = ValueParser(span=2)
        model = ValueParser(prefixes=(manufacturer,))
        pages = ChoiceParser(choices=("all", "page_a", "page_b", "page_c"), multiple=True)
        minimum_price = ValueParser(identifier=IntegerIdentifier, prefixes=("price",))
        maximum_results = ValueParser(suffixes=("results",), identifier=IntegerIdentifier)


class TestableEntityParserShouldIgnoreLeadAndTrailInEntities(_TestableEntityParserConfiguredIntent):
    lead = ("new",)
    trail = ("app",)
    ordered = True

    class EntityParser:
        name = ValueParser()




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
        return self.mock_intent.entities.get(entity_name)

    def parse_message_for_entities(self):
        # Truncate 'lead' and 'trail' from the message before parsing
        self.intent_reply = self.mock_intent.process(self.mock_message)
        self.mock_intent.entities = self.mock_intent.entities
        print(self.mock_intent.entities)


class TestEntityParserWithEmptyValueParser_ShouldSucceed(_TestBaseCase):

    mock_intent_cls = TestEntityParserWithTwoValueParsers
    mock_message = Message("some shopped item 695")

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
