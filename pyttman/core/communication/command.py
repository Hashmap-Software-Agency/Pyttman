
"""
File containing base classes related to binding
strings and sequences to logic, for defining a
set of rules on how natural language relates to
functions and methods.
"""
import abc
from abc import ABC
from itertools import zip_longest
from typing import List, Dict

from pyttman.core.communication.models.containers import Message, Reply
from pyttman.core.parsing.parsers import Parser


class AbstractCommand(abc.ABC):

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def respond(self, message: Message) -> Reply:
        """
        Subclasses overload this method to respond
        to a given command upon a match.

        The Command class is meant to be stateless.
        For replies that require context such as
        cache or other things related to other
        data, the use of a Caching backend is
        encouraged inside this method to
        store and retrieve information.
        """
        pass

    @abc.abstractmethod
    def matches(self, message: Message) -> bool:
        """
        Determine whether a Message matches a
        command instance. The 'lead' and 'trail'
        fields are traversed over and sought
        for matching strings.
        :param message: pyttman.Message object
        :return: bool, command matches or not
        """
        pass

    @abc.abstractmethod
    def _assert_ordered(self, message: list) -> bool:
        """
        Tells whether the Messgae content complies
        with the configuration of 'lead' and 'trail',
        thus meaning that all words defined in 'lead'
        and 'trail' shall occur in the same order in
        the message form the user, as they do in the
        'lead' and 'trail' tuples.
        :param message: Message object, from client
        :return: bool, message is ordered or not
        """
        """
        Truncates all strings which occurs in
        lead and trail.
        :param message: Pyttman.Message
        :return: list, truncated
        """
        pass

    @abc.abstractmethod
    def generate_help(self):
        """
        Generates a descriptive help_string message based
        on the docstring for the Command class the
        subclass has defined, as well as including
        the syntax for the command using the lead
        and trail fields.

        if the help_string is already defined, this
        help is used and no automated help is
        generated.
        :return:
        """
        pass


class BaseCommand(AbstractCommand, ABC):
    """
    Base class for a Command, containing configuration
    on which criterias are set for a message to match
    it, as well as methods to make understanding and
    retreiving data from a Message easier.

    Defining the Response internal class provides a
    class based way of handling how to respond to a
    Message. The user can interact with the internal
    methods such as
    """
    description = "Unavailable"
    example = None
    lead = tuple()
    trail = tuple()
    ordered = False
    help_string = None
    feature = None

    class InputStringParser:
        """
        Optional inner class to configure query strings
        in recieved messages which matches a Command.

        The identified values are stored in the
        'input_strings' dict.

        Class variables dictate the name of the key
        in which an identified value is placed under.
        """
        pass

    def __init__(self):
        if not isinstance(self.lead, tuple) or not isinstance(self.trail, tuple):
            raise AttributeError(f"'lead' and 'trail' fields must me tuples "
                                 f"containing strings for parsing to work "
                                 f"correctly")
        self.help_string = self.generate_help()
        self.name = _generate_name(self.__class__.__name__)
        self.input_strings = {}

    def __repr__(self):
        return f"{self.__class__.__name__}(lead={self.lead}, " \
               f"trail={self.trail}, ordered={self.ordered})"

    def matches(self, message: Message) -> bool:
        """
        Boolean indicator to whether the callback
        matches a given message, without returning
        the function itself as with the .Parse method.

        To begin with, the message has to match at least
        one word in the self.lead property. This is asserted
        through the .intersection method, as to get the word(s)
        that matches the self.lead property in a subset.
        Next, the optional self.trail property is investigated
        similarly if it is defined - otherwise not.

        The self.trail string / collection of strings has to,
        by definition, appear delay the words in self.lead.
        This is asserted by first identifying the words that
        matches the trail in the message. The words that also
        are present in the lead are removed by subtraction.
        Next, by iterating over the two collections the order
        of appearence can now be determined by identifying
        the index of the word compared between the two. If
        the index is higher in the trail than the lead, the
        loop continues and will eventually exhaust.
        If not, the trail condition is not met and method
        exits with False.

        :param message:
            pyttman.Message
        :returns:
            Bool, True if self matches command
        """

        match_trail = False

        sanitized = message.as_list(sanitized=True)

        if not (match_lead := [i for i in self.lead if i in sanitized]):
            return False
        elif self.ordered and not self._assert_ordered(sanitized):
            return False

        if self.trail:
            latest_lead_occurence, latest_trail_occurence = 0, 0

            if not (match_trail := [i for i in self.trail if i in sanitized]):
                return False

            for lead, trail in zip_longest(match_lead, match_trail):
                try:
                    _index = sanitized.index(lead)
                    if _index > latest_lead_occurence:
                        latest_lead_occurence = _index
                except ValueError:
                    pass
                try:
                    _index = sanitized.index(trail)
                    if _index > latest_trail_occurence:
                        latest_trail_occurence = _index
                except ValueError:
                    pass
            match_trail = (latest_trail_occurence > latest_lead_occurence)
        return match_lead and match_trail or match_lead and not self.trail

    def _assert_ordered(self, message: list) -> bool:
        ordered_trail, ordered_lead = True, True
        for word_a, word_b in zip([i for i in message if i in self.lead], self.lead):
            if word_a != word_b:
                ordered_lead = False
                break
        if not self.trail:
            return ordered_lead

        for word_a, word_b in zip([i for i in message if i in self.trail], self.trail):
            if word_a != word_b:
                ordered_trail = False
                break
        return ordered_trail and ordered_lead

    def truncated(self, message: Message):
        as_set = set([i.lower() for i in message.content])
        as_set -= set(self.lead)
        as_set -= set(self.trail)
        return list(as_set)

    def generate_help(self) -> str:
        if not self.help_string:
            help_string = f"\n* Help for command '{self.__class__.__name__}'\n" \
                          f"\n\t> Description:\n\t\t{self.description}\n" \
                          f"\n\t> Syntax:\n\t\t{'|'.join(self.lead)} {'|'.join(self.trail)}\n"
            if input_strings := list(self._get_input_string_parser_fields().keys()):
                help_string += f"\n\t> Information expected from the user:" \
                               f"\n\t\t{', '.join(input_strings)}\n"

            if self.example:
                help_string += f"\n\t> Example:\n\t\t'{self.example}'\n"
        else:
            help_string = self.help_string
        return f"{'-' * 50}{help_string}\n{'-' * 50}"

    def process(self, message: Message) -> Reply:
        """
        Iterate over all ValueParser objects and the name
        of the field it's allocated as.
        :param message: Message object
        :return: Reply, logic defined in the 'respond' method
        """
        for name, parser in self._get_input_string_parser_fields().items():
            # Let the ValueParser search for matching strings and set its value
            parser.parse_message(message)

            # Set query string values to None if none found
            if parser.value:
                self.input_strings[name] = parser.value
            else:
                self.input_strings[name] = None
        return self.respond(message=message)

    def _get_input_string_parser_fields(self) -> Dict[str, Parser]:
        """
        Returns a dict with all name:parser in the inner class
        'InputStringParser'
        :return: dict[str, Parser]
        """
        name_parser_map = {}
        for field_name in dir(self.InputStringParser):
            parser_object = getattr(self.InputStringParser, field_name)

            if not field_name.startswith("__") and isinstance(parser_object, Parser):
                name_parser_map[field_name] = parser_object
        return name_parser_map


class Command(BaseCommand):
    def respond(self, message: Message) -> Reply:
        raise NotImplementedError("The 'respond' method must be "
                                  "defined when subclassing Command")
