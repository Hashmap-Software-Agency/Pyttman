import unittest
from datetime import datetime

from pyttman import Feature
from pyttman.core.communication.command import Command
from pyttman.core.communication.models.containers import Reply, Message
from pyttman.core.parsing import parsers
from pyttman.core.parsing.identifiers import DateTimeFormatIdentifier


class SetTimeFormat(Command):
    description = "Sets the format of datetime outputs"
    lead = ("set",)
    trail = ("datetime", "format",)

    class InputStringParser:
        datetime_format = parsers.ValueParser(identifier=DateTimeFormatIdentifier)

    def respond(self, messsage: Message) -> Reply:
        if datetime_format := self.input_strings.get("datetime_format"):
            return Reply(f"Set datetime format to: {datetime_format}")


class GetLastItem(Command):
    lead = ("last",)

    class InputStringParser:
        last_word = parsers.PositionalParser()

    def respond(self, messsage: Message) -> Reply:
        return Reply(f"The last value was: "
                     f"{self.input_strings.get('last_word')}")


class GetTime(Command):
    description = "Returns the current time"
    lead = ("what",)
    trail = ("time",)

    def respond(self, messsage: Message) -> Reply:
        timestr = datetime.now().strftime(self.input_strings.get("datetime_format"))
        return Reply(f"The time is currently {timestr}")


class ClockFeature(Feature):
    """
    A basic, simple feature which
    answers what time it is.
    """
    commands = (GetTime, SetTimeFormat)


class TestCommand(unittest.TestCase):

    def test_value_parser(self):

        msg = Message("Set datetime format to %y-%m-%d")

        set_time_command = SetTimeFormat()

        if set_time_command.matches(msg):
            set_time_command.process(msg)

        print(set_time_command.input_strings)
        self.assertEqual(set_time_command.input_strings.get("datetime_format"),
                         "%y-%m-%d")
        print(set_time_command.generate_help())
        print(set_time_command.respond(messsage=msg).as_str())

    def test_positional_parser(self):

        get_last_item = GetLastItem()

        msg = Message("the last item is turtle")
        get_last_item.process(msg)

        print(get_last_item.input_strings)
        self.assertEqual(get_last_item.input_strings.get("last_word"), "turtle")

        print(get_last_item.respond(messsage=msg).as_str())
