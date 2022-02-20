import unittest
from unittest import TestCase

from pyttman.core.communication.models.containers import Message
from pyttman.core.entity_parsing import identifiers
from pyttman.core.entity_parsing.entity import Entity


class TestDateStringIdentifier(TestCase):

    def setUp(self) -> None:
        self.sample_message = Message("The biggest manmade disaster in human history "
                                      "occurred 1984/04/26-01:23:45 when the Chernobyl "
                                      "powerplant meltdown accident. Another big human "
                                      "made disaster is the hiroshima bomb which dropped "
                                      "over the city of Heroshima in Japan on 1945-08-06.")

    def test_identify_valid(self):
        identifier = identifiers.DateTimeStringIdentifier(start_index=0)

        # Expect to find an Entity with the following value on index 8
        expected_entity = Entity("1984/04/26-01:23:45", 8)
        found_entity = identifier.try_identify_entity(self.sample_message)
        self.assertEqual(expected_entity, found_entity)

    def test_identify_valid_entity_later_occurrence(self):
        identifier = identifiers.DateTimeStringIdentifier(start_index=9)

        # Expect to find an Entity with the following value on index 8
        expected_entity = Entity("1945-08-06.", 34)
        found_entity = identifier.try_identify_entity(self.sample_message)
        self.assertIsNotNone(found_entity)
