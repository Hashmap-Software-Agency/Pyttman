import re
from typing import Union

from pyttman.core.containers import MessageMixin
from pyttman.core.entity_parsing.entity import Entity


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
    The regex pattern is evaluated by the EntityFieldValueParser
    at runtime.
    """
    patterns = (r"^.*$",)
    min_length = None
    max_length = None
    start_index = 0

    def __init__(self, **kwargs):
        try:
            self.patterns = tuple([re.compile(pat) for pat in self.patterns])
        except Exception as e:
            raise AttributeError("Identifier pattern could not compile") from e
        [setattr(self, k, v) for k, v in kwargs.items()]

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

    def try_identify_entity(self, message: MessageMixin) -> Union[Entity,
                                                                  None]:
        """
        Evaluates if any element in the content of
        a Message object matches with its pattern.

        :return Entity: Element in message.content which matched
                     the pattern assigned, or None if none found
        """
        for pattern in self.patterns:
            try:
                for i, elem in enumerate(message.content[self.start_index:]):
                    if re.match(pattern, elem) and self\
                            ._assert_length_requirement(elem):
                        return Entity(value=elem,
                                      index_in_message=self.start_index + i)
            except IndexError:
                return None
        return None


class CellPhoneNumberIdentifier(Identifier):
    """ Identifies whether a string is similar to a cell number """
    patterns = (r"^(\d{3}.\d{4}.\d{3})|(\d{10})|(\d{3}.\d{3}.\d{4})$",)


class DateTimeStringIdentifier(Identifier):
    """ Identifies whether a string looks like a date string """
    patterns = (r"^(\d{4}).(\d{2})",
                r"^(\d{2}).(\d{2}).(\d{2})",
                r"^(\d{4}).(\d{2}).(\d{2}).(\d{2}):(\d).*$",
                r"^(\d{2}).(\d{2}).(\d{2}).(\d{2}):(\d{2}).*$")


class DateTimeFormatIdentifier(Identifier):
    """ identifies a datetime format configuration string """
    patterns = (r"^%.*$",)


class IntegerIdentifier(Identifier):
    """ identifies all integers """
    patterns = (r"[0-9]+",)


class CapitalizedIdentifier(Identifier):
    """
    This identifier class will target strings which
    are capitalized, meaning they begin with a capital
    letter.
    """
    patterns = (r"\b[A-Z][a-zA-Z]*\b",)


NumberIdentifier = IntegerIdentifier
FloatIdentifier = IntegerIdentifier
