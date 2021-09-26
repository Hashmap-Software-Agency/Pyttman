"""
This file contains mockup Commands, for testing and as
a demonstration of some of the functionality offered with
Class based Commands.
"""

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

#     MIT License
#
#
#      Permission is hereby granted, free of charge, to any person obtaining a copy
#      of this software and associated documentation files (the "Software"), to deal
#      in the Software without restriction, including without limitation the rights
#      to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#      copies of the Software, and to permit persons to whom the Software is
#      furnished to do so, subject to the following conditions:
#
#
import typing
from datetime import datetime
from typing import Union

from pyttman.core.ability import Ability
from pyttman.core.intent import Intent
from pyttman.core.communication.models.containers import Message, Reply, ReplyStream, MessageMixin
from pyttman.core.parsing import parsers, identifiers
from pyttman.core.parsing.identifiers import DateTimeFormatIdentifier, IntegerIdentifier, CapitalizedIdentifier, \
    CellPhoneNumberIdentifier, DateTimeStringIdentifier
from pyttman.core.parsing.parsers import ValueParser, ChoiceParser


"""
This file holds mockup Ability and Intent classes 
used in unit tests.
"""


class SetTimeFormat(Intent):
    description = "Sets the format of datetime outputs"
    lead = ("set",)
    trail = ("datetime", "format",)

    class EntityParser:
        datetime_format = parsers.ValueParser(identifier=DateTimeFormatIdentifier)

    def respond(self, message: Message) -> typing.Union[Reply, ReplyStream]:
        if datetime_format := self.entities.get("datetime_format"):
            return Reply(f"Set datetime format to: {datetime_format}")


class GetLastItem(Intent):
    lead = ("last",)

    class EntityParser:
        last_word = parsers.PositionalParser()

    def respond(self, message: Message) -> typing.Union[Reply, ReplyStream]:
        return Reply(f"The last value was: "
                     f"{self.entities.get('last_word')}")


class GetTime(Intent):
    description = "Returns the current time"
    lead = ("what",)
    trail = ("time",)

    def respond(self, message: Message) -> typing.Union[Reply, ReplyStream]:
        timestr = datetime.now().strftime(self.entities.get("datetime_format"))
        return Reply(f"The time is currently {timestr}")


class GetContactInfo(Intent):
    lead = ("get", "info", "details")
    trail = ("contactinfo", "contact")

    class EntityParser:
        name = parsers.PositionalParser(position=parsers.PositionalParser.last_item)

    def respond(self, message: Message) -> typing.Union[Reply, ReplyStream]:
        name = self.entities["name"]
        return Reply(f"Getting contact information for {name}")


class MockContact:
    def __init__(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items()]


class UpdateContactInfo(Intent):
    lead = ("update", "register")
    trail = ("number",)
    example = "register 1112222442 as new number for John"
    description = "Testing for parsers - Update contact info" \
                  "for given contact."

    class EntityParser:
        contact_name = parsers.ValueParser(identifier=identifiers.CapitalizedIdentifier)
        new_number = parsers.ValueParser(identifier=identifiers.CellPhoneNumberIdentifier)

    def respond(self, message: Message) -> typing.Union[Reply, ReplyStream]:
        contact_name = self.entities.get("contact_name")
        new_number = self.entities.get("new_number")
        contact = self.storage.get("contacts").get(contact_name)

        contact.number = new_number
        return Reply(f"Updated {contact.name}'s number to {new_number}")


class ContactsAbility(Ability):
    intents = (UpdateContactInfo, GetContactInfo)

    def configure(self):
        self.storage.put("contacts",
                         {"John": MockContact(name="John", number=1234567891)})


class ClockAbility(Ability):
    """
    A basic, simple feature which
    answers what time it is.
    """
    intents = (GetTime, SetTimeFormat)


class _TestableEntityParserConfiguredIntent(Intent):
    """
    Base class for entity parsing tests.
    """

    def respond(self, message: MessageMixin) -> Union[Reply, ReplyStream]:
        return Reply(self.entities)


class TestableEntityParserWithEmptyValueParser(_TestableEntityParserConfiguredIntent):
    """
    Tests the use of a single ValueParser without any configuration """

    class EntityParser:
        item = ValueParser()


class TestableEntityParserWithTwoValueParsers(_TestableEntityParserConfiguredIntent):
    """
    Tests the use of a single ValueParser without any configuration """

    class EntityParser:
        item = ValueParser(span=5)
        price = ValueParser(identifier=IntegerIdentifier)


class TestableEntityParserUsingOnlyPreAndSuffixes_Multiple(_TestableEntityParserConfiguredIntent):
    """
    Intent class for testing Intent matching
    and Entity Parsing, specifically without
    identifiers but only using pre / suffixes.
    """

    class EntityParser:
        exclude = ("on", "and")
        song = ValueParser(span=10)
        artist = ValueParser(prefixes=("by", "with"), span=10)
        platform = ChoiceParser(choices=("Spotify", "SoundCloud"), multiple=True)


class TestableEntityParserUsingOnlyPreAndSuffixes_Single(_TestableEntityParserConfiguredIntent):
    """
    Intent class for testing Intent matching
    and Entity Parsing, specifically without
    identifiers but only using pre / suffixes.
    """

    class EntityParser:
        exclude = ("on", "and")
        song = ValueParser(span=10)
        artist = ValueParser(prefixes=("by", "with"), span=10)
        platform = ChoiceParser(choices=("Spotify", "SoundCloud"))


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