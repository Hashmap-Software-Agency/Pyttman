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
from unittest import TestCase

from pyttman.core.communication.models.containers import Message
from pyttman.core.parsing.routing import FirstMatchingRouter
from tests.mockups import ContactsAbility, GetContactInfo

##############################
#         T E S T S          #
##############################


class TestIntentProducesCorrectReply(TestCase):

    def setUp(self) -> None:
        self.router = FirstMatchingRouter([ContactsAbility()], ["response-unknown"], "help")

    def test_update_contact(self):
        test_msg = Message("register 0701111234 as new number for John")
        reply = self.router.get_reply(test_msg)
        self.assertEqual("Updated John's number to 0701111234", reply.as_str(),
                         "Reply did not match expected output.")

    @unittest.skip
    def test_get_contact_by_last_item(self):
        result = self.router.get_reply(Message("Get contact info for John"))
        self.assertEqual(result.as_str(), "Getting contact information for John")


class TestPositionalParser(TestCase):
    def setUp(self) -> None:
        self.get_contact = GetContactInfo()

