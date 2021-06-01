import re
from typing import Optional

from pyttman.core.communication.models.containers import Message


class Identifier:
    """
    Base class for an Identifier.

    The Identifier class aids in identifying
    strings based on their patterns, as in
    if they contain integers, special characters,
    whether they are capitalized, have a date-like
    format to them, and alike.

    Subclasses can define very granularly how
    a string can look by strict rules, or less
    so with less defined criterias.

    The Identifier will use regex to assess
    the similarity of given string.

    This class is subclassed and patterns are
    defined in the tuple 'patterns' as raw
    python strings (prepend the string with 'r').
    The regex pattern is evaluated by the Parser
    at runtime.
    """
    patterns = (r"^.*$",)

    def __init__(self):
        self.matches: bool = False
        self.matching_string = None
        try:
            self.patterns = tuple([re.compile(pat) for pat in self.patterns])
        except Exception as e:
            raise AttributeError("Identifier pattern could not compile") from e

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"patterns={self.patterns}, " \
               f"matches={self.matches}, " \
               f"matching_string={self.matching_string})"

    def get_matching_string(self, message: Message) -> Optional[str]:
        """
        Evaluates if any element in the content of
        a Message object matches with its pattern.

        :return bool: One of the patterns defined in
        self.patterns matched a string in Message.content
        """
        for pattern in self.patterns:
            for elem in message.content:
                if re.match(pattern, elem):
                    self.matching_string = elem
                    return elem
        return None


class CellPhoneNumberIdentifier(Identifier):
    """ Identifies whether a string is similar to a datetime """
    patterns = (r"^(\d{3}.\d{4}.\d{3})|(\d{10})|(\d{3}.\d{3}.\d{4})$",)


class DateTimeStringIdentifier(Identifier):
    """ Identifies whether a string looks like a date string """
    patterns = (r"^(\d{4}).(\d{2}).(\d{2}).(\d{2}):(\d{2}).*$",
                r"^(\d{2}).(\d{2}).(\d{2}).(\d{2}):(\d{2}).*$")


class DateTimeFormatIdentifier(Identifier):
    """ identifies a datetime format configuration string """
    patterns = (r"^%.*$",)
