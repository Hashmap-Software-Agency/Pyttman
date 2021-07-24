from unittest import TestCase
import pyttman
import testing_project.settings as settings
from tests.mockups import ContactFeature

pyttman.load_settings(settings)

from pyttman.core.communication.models.containers import Message
from pyttman.core.parsing.routing import FirstMatchingRouter


class TestLinearSearchFirstMatchingRouter(TestCase):
    def test_reply(self):
        update_contact_message = Message("register 1112222442 as new number for John")
        contact_feature = ContactFeature()
        router = FirstMatchingRouter()
        router.features = (contact_feature,)
        self.assertEqual(router.get_reply(message=update_contact_message).as_list(),
                         ['Updated', "John's", 'number', 'to', '1112222442'])
