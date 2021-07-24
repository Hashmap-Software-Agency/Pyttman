import unittest

from pyttman.core.communication.models.containers import Message
from tests.mockups import SetTimeFormat, GetLastItem


class TestCommand(unittest.TestCase):

    def test_value_parser(self):

        msg = Message("Set datetime format to %y-%m-%d")

        set_time_command = SetTimeFormat()

        if set_time_command.matches(msg):
            set_time_command.process(msg)

        print(set_time_command.entities)
        self.assertEqual(set_time_command.entities.get("datetime_format"),
                         "%y-%m-%d")
        print(set_time_command.generate_help())
        print(set_time_command.respond(messsage=msg).as_str())

    def test_positional_parser(self):

        get_last_item = GetLastItem()

        msg = Message("the last item is turtle")
        get_last_item.process(msg)

        print(get_last_item.entities)
        self.assertEqual(get_last_item.entities.get("last_word"), "turtle")

        print(get_last_item.respond(messsage=msg).as_str())
