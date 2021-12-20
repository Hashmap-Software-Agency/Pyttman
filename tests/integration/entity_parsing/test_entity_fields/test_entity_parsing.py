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
