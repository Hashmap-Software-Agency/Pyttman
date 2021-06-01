
"""
File containing base classes related to binding
strings and sequences to logic, for defining a
set of rules on how natural language relates to
functions and methods.
"""
import abc
from abc import ABC
from itertools import zip_longest

from pyttman.core.communication.models.containers import Message, Reply
from pyttman.core.parsing.parsers import Parser


class AbstractCommand(abc.ABC):

    IGNORED_CHARS = '?=)(/&%¤#"!,.-;:_^*`´><|'

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def respond(self, messsage: Message) -> Reply:
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
    def truncate(self, message: Message):
        """
        Truncates all strings which occurs in
        lead and trail.
        :param message: Pyttman.Message
        :return: None
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
    description = __name__
    example = str()
    lead = tuple()
    trail = tuple()
    ordered = False
    help_string = "Unavailable"

    class QueryStringParser:
        """
        Optional inner class to configure query strings
        in recieved messages which matches a Command.

        The identified values are stored in the
        'query_strings' dict.

        Class variables dictate the name of the key
        in which an identified value is placed under.

        Sometimes values are provided in a message
        without a clear prefix or suffix to identify
        the value itself. For these edge cases, a few
        magic strings are available

        There are a few config strings for this
        available, defined below.

        '$lastitem' - the last element in the message
        '$firstitem' - the first element in the message
        '$timestr'

        :example:
            class ValueParser:
                color = parsers.ValueParser(keys=("color", "colors"), )
        """
        pass

    def __init__(self):
        if not isinstance(self.lead, tuple) or not isinstance(self.trail, tuple):
            raise AttributeError(f"'lead' and 'trail' fields must me tuples "
                                 f"containing strings for parsing to work "
                                 f"correctly")
        self.help_string = self.generate_help()
        self.query_strings = {}

    def __repr__(self):
        return f"{self.__class__.__name__}(lead={self.lead}, " \
               f"trail={self.trail}, ordered={self.ordered}, " \
               f"help_string={self.help_string})"

    def matches(self, message: Message) -> bool:
        """
        Boolean indicator to whether the callback
        matches a given message, without returning
        the function itself as with the .Parse method.

        Return the callable bound to the Callback instance
        if the message matches the subset(s) of strings
        defined in this object.

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

        lowered = [i.lower().strip(Command.IGNORED_CHARS)
                   for i in message.content]

        if not (match_lead := [i for i in self.lead if i in lowered]):
            return False
        elif self.ordered and not self._assert_ordered(lowered):
            return False

        if self.trail:
            latest_lead_occurence, latest_trail_occurence = 0, 0

            if not (match_trail := [i for i in self.trail if i in lowered]):
                return False

            for lead, trail in zip_longest(match_lead, match_trail):
                try:
                    _index = lowered.index(lead)
                    if _index > latest_lead_occurence:
                        latest_lead_occurence = _index
                except ValueError:
                    pass
                try:
                    _index = lowered.index(trail)
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

    def truncate(self, message: Message):
        as_set = set([i.lower() for i in message.content])
        as_set -= self.lead
        as_set -= self.trail
        message.content = list(as_set)

    def generate_help(self) -> str:
        help_string = f"\nHelp for command {self.__class__.__name__}\n" \
                      f"\n\t* Description: {self.description}" \
                      f"\n\t* Syntax: [{'|'.join(self.lead)}] [{'|'.join(self.trail)}]"

        return f"{'=' * 50}{help_string}\n{'=' * 50}"

    def parse_for_query_strings(self, message: Message) -> None:
        """
        Iterate over all ValueParser objects and the name
        of the field it's allocated as.
        :param message: Message object
        :return: None
        """
        for query_string_name in dir(self.QueryStringParser):
            query_string_obj = getattr(self.QueryStringParser, query_string_name)

            # Put the value of the ValueParser behind its name in the query_strings dict, if found
            if not query_string_name.startswith("__") and not callable(query_string_obj) \
                    and isinstance(query_string_obj, Parser):

                # Let the ValueParser search for matching strings and set its value
                query_string_obj.parse_message(message)

                # Set query string values to None if none found
                if query_string_obj.value:
                    self.query_strings[query_string_name] = query_string_obj.value
                else:
                    self.query_strings[query_string_name] = None


class Command(BaseCommand):
    def respond(self, messsage: Message) -> Reply:
        raise NotImplementedError
