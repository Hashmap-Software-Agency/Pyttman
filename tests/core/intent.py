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
from typing import Type
from unittest import TestCase

from ordered_set import OrderedSet

from pyttman.core.communication.models.containers import Message
from pyttman.core.intent import Intent
import tests.mockups as mockups


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

        # Truncate 'lead' and 'trail' from the message before parsing
        self.mock_message.truncate(self.mock_intent.lead + self.mock_intent.trail)

    def get_entity_value(self, entity_name):
        return self.mock_intent.entities.get(entity_name)

    def parse_message_for_entities(self):
        # Truncate 'lead' and 'trail' from the message before parsing
        self.intent_reply = self.mock_intent.process(self.mock_message)
        self.mock_intent.entities = self.mock_intent.entities
        print(self.mock_intent.entities)


class TestEntityParserWithEmptyValueParser_ShouldSucceed(_TestBaseCase):

    mock_intent_cls = mockups.TestableEntityParserWithTwoValueParsers
    mock_message = Message("some shopped item 695")

    def test_respond(self):
        self.parse_message_for_entities()
        self.assertEqual("some shopped item", self.get_entity_value("item"))
        self.assertEqual("695", self.get_entity_value("price"))


class TestEntityParserPrefixesAndSuffixes_ChoiceParserMultiple_ShouldSucceed(_TestBaseCase):

    mock_intent_cls = mockups.TestableEntityParserUsingOnlyPreAndSuffixes_Multiple
    mock_message = Message("man in the mirror with michael "
                           "jackson on spotify and SOUNDCLOUD")

    def test_respond(self):
        self.parse_message_for_entities()
        self.assertEqual("man in the mirror", self.get_entity_value("song"))
        self.assertEqual("michael jackson", self.get_entity_value("artist"))
        self.assertEqual(OrderedSet(("SoundCloud", "Spotify")),
                         self.get_entity_value("platform"))


class TestEntityParserPrefixesAndSuffixes_ChoiceParserSingle_ShouldSucceed(_TestBaseCase):

    mock_intent_cls = mockups.TestableEntityParserUsingOnlyPreAndSuffixes_Single
    mock_message = Message("Shine On You Crazy Diamond by Pink Floyd on spoTifY")

    def test_respond(self):
        self.parse_message_for_entities()
        self.assertEqual("Shine On You Crazy Diamond", self.get_entity_value("song"))
        self.assertEqual("Pink Floyd", self.get_entity_value("artist"))
        self.assertEqual("Spotify", self.get_entity_value("platform"))


class TestEntityParserPrefixesAndSuffixes_2_ShouldSucceed(_TestBaseCase):

    mock_intent_cls = mockups.TestableEntityParserUsingOnlyPreAndSuffixes_Single
    mock_message = Message("Stand By Me with Ben E. King on Soundcloud")

    def test_respond(self):
        self.parse_message_for_entities()
        self.assertEqual("Stand By Me", self.get_entity_value("song"))
        self.assertEqual("SoundCloud", self.get_entity_value("platform"))


class TestEntityParserIdentifiers_ShouldSucceed(_TestBaseCase):

    mock_intent_cls = mockups.TestableEntityParserIntentUsingIdentifier
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

    mock_intent_cls = mockups.TestableEntityParserIntentUsingIdentifierAndPrefixesSuffixes
    mock_message = Message("create a new contact Will "
                           "Byers on mobile with 0805552859 "
                           "and do it on 2021-09-20-10:40")

    def test_respond(self):
        self.parse_message_for_entities()

        self.assertIsNone(self.get_entity_value("contact"))
        self.assertIsNone(self.get_entity_value("number"))
        self.assertIsNone(self.get_entity_value("date"))


class TestEntityParserIdentifiersPrefixesSuffiixes_ShouldSucceed(_TestBaseCase):

    mock_intent_cls = mockups.TestableEntityParserIntentUsingIdentifierAndPrefixesSuffixes
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

    mock_intent_cls = mockups.TestableEntityParserIdentifiersAndSuffixes_FoodMessage_ShouldSucceed
    mock_message = Message("search for vegetarian recipes on all websites "
                           "max ingredients 10 and 4 servings on RestaurantName")

    def test_respond(self):
        self.parse_message_for_entities()

        self.assertEqual("vegetarian", self.get_entity_value("preference"))
        self.assertEqual("10", self.get_entity_value("max_ingredients"))
        self.assertEqual("4", self.get_entity_value("servings"))
        self.assertEqual("RestaurantName", self.get_entity_value("restaurant"))


class TestEntityParserIDentifierPrefixesSuffixesMultipleChoices_3_ShouldSucceed(_TestBaseCase):

    mock_intent_cls = mockups.TestableEntityParserIdentifiersAndSuffixes_AdvertisementMessage_ShouldSucceed
    mock_message = Message("Search for ManufacturerA ManufacturerB Model123 "
                           "on page_a and page_b price 45000 60 results")

    def test_respond(self):
        self.parse_message_for_entities()

        self.assertEqual("ManufacturerA ManufacturerB", self.get_entity_value("manufacturer"))
        self.assertEqual("Model123", self.get_entity_value("model"))
        self.assertEqual(OrderedSet(['page_b', 'page_a']), self.get_entity_value("pages"))
        self.assertEqual("60", self.get_entity_value("maximum_results"))
        self.assertEqual("45000", self.get_entity_value("minimum_price"))
