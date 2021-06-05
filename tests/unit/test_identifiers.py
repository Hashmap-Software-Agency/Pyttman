from unittest import TestCase

from pyttman.core.communication.models.containers import Message
from pyttman.core.parsing import identifiers


class TestDateStringIdentifier(TestCase):

    def setUp(self) -> None:
        self.invalid_strings = ("2432-66-f3 0033",
                                "1999-001-21:20:40:50",
                                "1998/09/13-f3:00")

        self.valid_strings = ("2021-07-25-09:00",
                              "2021/07/31-09:00")

    def test_identify_valid(self):
        for string in self.valid_strings:
            identifier = identifiers.DateTimeStringIdentifier()
            self.assertEqual(string, identifier.get_matching_string(Message(string)))

    def test_identify_invalid(self):
        for string in self.invalid_strings:
            identifier = identifiers.DateTimeStringIdentifier()
            self.assertIsNone(identifier.get_matching_string(Message(string)))
