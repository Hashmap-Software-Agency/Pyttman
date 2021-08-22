from unittest import TestCase

import pyttman
from pyttman.core.communication.models.containers import Message
from testing_project import settings as settings
from tests.mockups import ContactFeature, GetContactInfo

pyttman.load_settings(settings)


##############################
#         T E S T S          #
##############################


class TestValueParser(TestCase):

    def test_update_contact(self):
        update_contact_message = Message("register 1112222442 as new number for John")
        contact_feature = ContactFeature()
        for command in contact_feature.intents:
            if command.matches(message=update_contact_message):
                response = command.process(message=update_contact_message)
                print(response)


class TestPositionalParser(TestCase):
    def setUp(self) -> None:
        self.get_contact = GetContactInfo()

    def test_get_contact_by_last_item(self):
        result = self.get_contact.process(Message("Get contact info for John"))
        self.assertEqual(result.as_str(), "Getting contact information for John")
