#  MIT License
#
#  Copyright (c) 2021-present Simon Olofsson
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#   in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.

from typing import Union

from pyttman.core.communication.models.containers import MessageMixin, Reply, \
    ReplyStream
from pyttman.core.intent import Intent
from pyttman.core.parsing.fields import TextEntityField, IntegerEntityField, \
    FloatEntityField
from pyttman.core.parsing.identifiers import CapitalizedIdentifier, \
    CellPhoneNumberIdentifier, DateTimeStringIdentifier, IntegerIdentifier
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


class TestableEntityParserIntentUsingIdentifierAndPrefixesSuffixes_CapitalizedChoices(_TestableEntityParserConfiguredIntent):
    """
    Intent class for testing Intent matching and Entity
    parsing, using identifiers AND pre/suffixes.

    Testing ChoiceParser with capitalized choices.
    """

    class EntityParser:
        month = ChoiceParser(choices=("January", "February", "Mars", "April", "May",
                                      "June", "July", "August", "September",
                                      "October", "November", "December"))


class TestableEntityParserIdentifiersAndSuffixes_FoodMessage_ShouldSucceed(_TestableEntityParserConfiguredIntent):
    class EntityParser:
        restaurant = ValueParser(identifier=CapitalizedIdentifier, span=5)
        preference = ChoiceParser(choices=("vegetarian", "meatarian"))
        max_ingredients = ValueParser(prefixes=("ingredients",), identifier=IntegerIdentifier)
        servings = ValueParser(suffixes=("servings",), identifier=IntegerIdentifier)


class TestableEntityParserIdentifiersAndSuffixes_AdvertisementMessage_ShouldSucceed(_TestableEntityParserConfiguredIntent):
    lead = ("search",)
    trail = ("for", "after")

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


class TestableEntityParserWithTwoValueParsers(_TestableEntityParserConfiguredIntent):
    """
    Tests the use of a single ValueParser without any configuration """
    lead = ("new", "add")
    trail = ("expense", "purchase")

    class EntityParser:
        item = ValueParser(span=10)
        price = ValueParser(identifier=IntegerIdentifier)


class TestableEntityParserWithIntAndStringField(_TestableEntityParserConfiguredIntent):
    """
    Tests the use of a single ValueParser without any configuration """
    lead = ("new", "add")
    trail = ("expense", "purchase")

    class EntityParser:
        item = TextEntityField(span=10, )
        price = FloatEntityField(prefixes=("price",))


class TestableEntityParserValidStrings(_TestableEntityParserConfiguredIntent):
    """
    Tests the use of a single ValueParser without any configuration """
    lead = ("new", "add")
    trail = ("expense", "purchase")

    class EntityParser:
        item = TextEntityField(valid_strings=("food", "clothes"))
        price = FloatEntityField(prefixes=("price",))
