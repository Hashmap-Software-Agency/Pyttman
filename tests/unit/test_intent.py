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
from typing import Union
from unittest import TestCase

from pyttman.core.communication.models.containers import Message, MessageMixin, Reply, ReplyStream
from pyttman.core.intent import Intent
from pyttman.core.parsing.parsers import ValueParser, ChoiceParser


class PlaySongIntent(Intent):
    """
    Intent class for testing Intent matching
    and Entity Parsing.
    """
    lead = ("play",)

    class EntityParser:
        exclude = ("on",)
        song = ValueParser(span=10)
        artist = ValueParser(prefixes=("by",))
        platform = ChoiceParser(choices=("spotify", "soundcloud"))

    def respond(self, message: MessageMixin) -> Union[Reply, ReplyStream]:
        return Reply(self.entities)


class TestEntityParser(TestCase):

    def setUp(self) -> None:
        self.mock_intent = PlaySongIntent()
        self.mock_message = Message("play man in the mirror by MJ on spotify")

        # Truncate 'lead' and 'trail' from the message before parsing
        self.mock_message.truncate(self.mock_intent.lead + self.mock_intent.trail)

    def test_respond(self):
        self.mock_intent._entity_parser.parse_message(self.mock_message)
        print("ENTITY_PARSER VALUES: ", self.mock_intent._entity_parser.value)

        self.assertEqual("man in the mirror", self.mock_intent._entity_parser.value["song"])
        self.assertEqual("spotify", self.mock_intent._entity_parser.value["platform"])
