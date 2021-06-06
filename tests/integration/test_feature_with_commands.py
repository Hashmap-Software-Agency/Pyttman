from unittest import TestCase

import pyttman
from example_project.example_app import settings

pyttman.load_settings(settings)

from pyttman.core.communication.command import Command
from pyttman.core.communication.models.containers import Message, Reply
from pyttman.core.parsing import parsers, identifiers
from pyttman import Feature


##############################
#       M O C K U P S        #
##############################


class MockContact:
    def __init__(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items()]


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
        new_number = self.input_strings["number"]

        contact = self.feature.storage.get("contacts").get(name)
        contact.number = new_number

        return Reply(f"Updated {name}'s number to {new_number}")


class GetContactInfo(Command):
    lead = ("get", "info", "details")
    trail = ("contactinfo", "contact")

    class InputStringParser:
        name = parsers.PositionalParser(position=parsers.PositionalParser.last_item)

    def respond(self, message: Message) -> Reply:
        name = self.input_strings["name"]
        return Reply(f"Getting contact information for {name}")


class ContactFeature(Feature):
    commands = (UpdateContactInfo(), GetContactInfo())

    def configure(self):
        self.storage.put("contacts", {"John": MockContact(name="John", number=1234567891)})


##############################
#         T E S T S          #
##############################


class TestValueParser(TestCase):

    def test_update_contact(self):
        update_contact_message = Message("register 1112222442 as new number for John")
        contact_feature = ContactFeature()
        for command in contact_feature.commands:
            if command.matches(message=update_contact_message):
                response = command.process(message=update_contact_message)
                print(response)


class TestPositionalParser(TestCase):
    def setUp(self) -> None:
        self.get_contact = GetContactInfo()

    def test_get_contact_by_last_item(self):
        result = self.get_contact.process(Message("Get contact info for John"))
        self.assertEqual(result.as_str(), "Getting contact information for John")
