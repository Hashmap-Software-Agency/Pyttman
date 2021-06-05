from unittest import TestCase

from pyttman.core.communication.command import Command
from pyttman.core.communication.models.containers import Message, Reply
from pyttman.core.parsing import parsers, identifiers


class UpdateContactInfo(Command):
    lead = ("update", "register")
    trail = ("number",)
    example = "register 1112222442 as new number for John"
    description = "Testing for parsers - Update contact info" \
                  "for given contact."

    class InputStringParser:
        number_by_identifier = parsers.ValueParser(identifier=identifiers.CellPhoneNumberIdentifier)
        number = parsers.ValueParser(prefixes=("register",), suffixes=("as",))
        name = parsers.ValueParser(identifier=identifiers.NameIdentifier)

    def respond(self, message: Message) -> Reply:
        name = self.input_strings["name"]
        number = self.input_strings["number"]
        return Reply(f"Updated {name}'s number to {number}")


class GetContactInfo(Command):
    lead = ("get", "info", "details")
    trail = ("contactinfo", "contact")

    class InputStringParser:
        name = parsers.PositionalParser(position=parsers.PositionalParser.last_item)

    def respond(self, message: Message) -> Reply:
        name = self.input_strings["name"]
        return Reply(f"Getting contact information for {name}")


class TestValueParser(TestCase):
    def setUp(self) -> None:
        self.update_phone_number = UpdateContactInfo()

    def test_update_contact(self):
        update_contact_message = Message("register 1112222442 as new number for John")
        if self.update_phone_number.matches(update_contact_message):

            print(self.update_phone_number.process(update_contact_message).as_str())

            self.assertEqual("1112222442",
                             self.update_phone_number.input_strings.get("number_by_identifier"))

            print(self.update_phone_number.input_strings)

            self.assertEqual({'name': 'John', 'number': '1112222442', 'number_by_identifier': '1112222442'},
                             self.update_phone_number.input_strings)
            self.assertEqual("1112222442", self.update_phone_number.input_strings.get("number"))
            self.assertEqual("Updated John's number to 1112222442",
                             self.update_phone_number.process(update_contact_message).as_str())

            print(self.update_phone_number.generate_help())


class TestPositionalParser(TestCase):
    def setUp(self) -> None:
        self.get_contact = GetContactInfo()

    def test_get_contact_by_last_item(self):
        result = self.get_contact.process(Message("Get contact info for John"))
        self.assertEqual(result.as_str(), "Getting contact information for John")
