from unittest import TestCase

from pyttman.core.communication.command import Command
from pyttman.core.communication.models.containers import Message, Reply
from pyttman.core.parsing import parsers, identifiers


class UpdatePhoneNumberCommand(Command):
    description = "Testing for parsers"
    lead = ("update", "register")
    trail = ("number",)
    example = "register 111444555 as new number for John"

    class InputStringParser:
        number = parsers.ValueParser(prefixes=("register",),
                                     suffixes=("as",))
        name = parsers.ValueParser(identifier=identifiers.NameIdentifier)

    def respond(self, messsage: Message) -> Reply:
        name = self.input_strings["name"]
        number = self.input_strings["number"]
        return Reply(f"Updated {name}'s number to {number}")


class TestValueParser(TestCase):
    def setUp(self) -> None:
        self.update_phone_number = UpdatePhoneNumberCommand()
        self.suffix_triggered = Message("It's supposed to be good weather")

    def test_update_contact(self):
        update_contact_message = Message("register 111444555 as new number for John")
        if self.update_phone_number.matches(update_contact_message):

            print(self.update_phone_number.process(update_contact_message).as_str())
            print(self.update_phone_number.input_strings)

            self.assertEqual({'name': 'John', 'number': '111444555'},
                             self.update_phone_number.input_strings)
            self.assertEqual("111444555", self.update_phone_number.input_strings.get("number"))
            self.assertEqual("Updated John's number to 111444555",
                             self.update_phone_number.process(update_contact_message).as_str())

            print(self.update_phone_number.generate_help())

    def test_suffix_only(self):
        pass
