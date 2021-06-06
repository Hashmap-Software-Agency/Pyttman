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
    example = "Set the datetime format to %m-%d-%y::%H:%M"

    class InputStringParser:
        datetime_format = parsers.ValueParser(identifier=DateTimeFormatIdentifier)

    def respond(self, message: Message) -> Reply:
        # Check the input_strings dict, populated by the InputStringParser
        if datetime_format := self.input_strings.get("datetime_format"):

            # Accessing the Feature-scope Storage object
            self.feature.storage.put("datetime_format", datetime_format)
            return Reply(f"Set datetime format to: {datetime_format}")


class GetTime(Command):
    description = "Returns the current time"
    lead = ("what",)
    trail = ("time",)
    example = "What time is it?"

    def respond(self, message: Message) -> Reply:
        timestr = datetime.now().strftime(self.input_strings.get("datetime_format"))
        return Reply(f"The time is currently {timestr}")


class ClockFeature(Feature):
    """
    A basic, simple feature which
    answers what time it is.
    """
    commands = (GetTime(), SetTimeFormat())

    def configure(self):
        self.storage.put("datetime_format", "%y-%m-%d - %H:%M")
