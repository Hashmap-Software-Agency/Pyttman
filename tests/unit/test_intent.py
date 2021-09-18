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

from pyttman.core.communication.models.containers import Message, MessageMixin, Reply, ReplyStream
from pyttman.core.intent import Intent
from pyttman.core.parsing.identifiers import CapitalizedIdentifier, CellPhoneNumberIdentifier, DateTimeStringIdentifier
from pyttman.core.parsing.parsers import ValueParser, ChoiceParser


class _TestableEntityParserConfiguredIntent(Intent):
    """
    Base class for entity parsing tests.
    """

    def respond(self, message: MessageMixin) -> Union[Reply, ReplyStream]:
        return Reply(self.entities)


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


## Unit tests ##


class _TestBaseCase(TestCase):
    """
    Base class for a test case testing EntityParser configurations
    """
    mock_intent_cls: Type[Intent]
    mock_message: Message

    def setUp(self) -> None:
        self.mock_intent = self.mock_intent_cls()

        # Truncate 'lead' and 'trail' from the message before parsing
        self.mock_message.truncate(self.mock_intent.lead + self.mock_intent.trail)

    def get_entity_value(self, entity_name):
        return self.mock_intent.entities.get(entity_name)

    def parse_message_for_entities(self):
        # Truncate 'lead' and 'trail' from the message before parsing
        self.mock_message.truncate(self.mock_intent.lead + self.mock_intent.trail)
        self.mock_intent._entity_parser.parse_message(self.mock_message)
        self.mock_intent.entities = self.mock_intent._entity_parser.value
        print(self.mock_intent.entities)


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