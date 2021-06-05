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
    min_length = None
    max_length = None

    def __init__(self):
        try:
            self.patterns = tuple([re.compile(pat) for pat in self.patterns])
        except Exception as e:
            raise AttributeError("Identifier pattern could not compile") from e

    def __repr__(self):
        return f"{self.__class__.__name__}(patterns={self.patterns})"

    def _assert_length_requirement(self, value: str) -> bool:
        """
        Assert the element identified complies
        with min_length and max_length fields
        :param value: str, value to me examined
        :return: bool, complies with both min_value and
                 max_value or not. if min_value and/or
                 max_value is omitted, they are considered
                 compliant in all situations, bypassing any
                 length of strings.
        """
        return ((len(value) > self.min_length
                 if self.min_length is not None else True) and
                (len(value) < self.max_length
                 if self.max_length is not None else True))

    def get_matching_string(self, message: Message) -> Optional[str]:
        """
        Evaluates if any element in the content of
        a Message object matches with its pattern.

        :return str: Element in message.content which matched
        the pattern assigned
        """

        identified_elem = None

        for pattern in self.patterns:
            for elem in message.content:
                if re.match(pattern, elem):
                    if self._assert_length_requirement(elem):
                        identified_elem = elem
        return identified_elem


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


class IntegerIdentifier(Identifier):
    """ identifies all integers """
    patterns = (r"[0-9]+",)


class NameIdentifier(Identifier):
    """ identifies names by looking for capitalized strings """
    patterns = (r"^([A-Z][a-z]*)$",)
