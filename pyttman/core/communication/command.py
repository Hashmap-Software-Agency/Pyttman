"""
File containing base classes related to binding
strings and sequences to logic, for defining a
set of rules on how natural language relates to
functions and methods.
"""
import abc
from abc import ABC
from itertools import zip_longest
from typing import List, Dict, Tuple

from pyttman.core.communication.models.containers import MessageMixin, Reply
from pyttman.core.internals import _generate_name, _generate_error_entry
from pyttman.core.parsing.parsers import Parser, ChoiceParser, EntityParserBase


class AbstractCommand(abc.ABC):

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def respond(self, message: MessageMixin) -> Reply:
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
    def matches(self, message: MessageMixin) -> bool:
        """
        Determine whether a MessageMixin matches a
        command instance. The 'lead' and 'trail'
        fields are traversed over and sought
        for matching strings.
        :param message: pyttman.MessageMixin object
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

    @abc.abstractmethod
    def truncate_message(self, message: MessageMixin) -> List[str]:
        """
        Truncates all strings which occurs in
        lead and trail.
        :param message: Pyttman.MessageMixin
        :return: list, truncate_message
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
    retreiving data from a message easier.

    The Command class is similar to an endpoint method
    in MVC, where it will recieve a Message objects
    upon a matching route given by the MessageRouter.

    :field lead:
        Define single strings or a sequence of strings in
        the 'lead' tuple, to define which words shall
        occur in the message for it to match on the
        Command instance. Selection is  'any of'.

    :field trail:
        Optional: define the 'trail' tuple.
        Similar to the 'lead' tuple - define a single, or
        a sequence of strings which will dictate which
        messages matches the Command. All strings defined
        in the 'trail' tuple must occur AFTER all strings
        defined in 'lead', for the command to match.
        This is useful to steer things such as 'search'
        as a lead keyword, in to the right command for
        the right 'search'. You may have one command
        for 'search for movies' and another for
        'search for the best coffee', in your app.

    :field ordered:
        Remember that all strings in 'lead' and 'trail'
        are 'any of'? That also means that Pyttman will not
        consider their order of appearence left- to right
        in the message compared to your lead and trail
        tuples. This can be set however with the 'ordered'
        parameter, to True. This will require that all
        strings defined in lead and trail, ocurr in the
        same order as you have defined them

    :field help_string:
        An optional help string which will override the
        auto-generated string that Pyttman builds for
        the user at run time.

    :field description:
        A human friendly piece of text to describe
        what your command does.

    :field example:
        Provide your users with an example of how
        a message for this command could look.
    """
    description: str = "Unavailable"
    example: str = None
    lead: Tuple[str] = tuple()
    trail: Tuple[str] = tuple()
    ordered: bool = False
    help_string: str = None
    feature = None

    class EntityParser(EntityParserBase):
        """
        Optional inner class to configure query strings
        in recieved messages which matches a Command.

        The identified values are stored in the
        'entities' dict, and are also available
        in the variable which the ValueParser is assigned
        to under the 'value' field.

        Class variables dictate the name of the key
        in which an identified value is placed under.

        > example:
            first_name = ValueParser(identifier=CapitalizedIdentifier)
            last_name = ValueParser(identifier=CapitalizedIdentifier,
                                    prefixes=(firstname,))

        In a given message based on the command:
            "My name is John Doe, what's yours?"
        .. the inut_strings field in the Command would look like:
            `{"first_name": "John", "last_name": "doe"}`
        .. This is because we specified that the last name
        has to occur after the first name, with the "prefixes"
        argument, and using the first name as that condition.
        """
        pass

    def __init__(self, **kwargs):
        if not isinstance(self.lead, tuple) or not isinstance(self.trail, tuple):
            raise AttributeError(f"'lead' and 'trail' fields must me tuples "
                                 f"containing strings for parsing to work "
                                 f"correctly")
        [setattr(self, k, v) for k, v in kwargs.items()]
        self.name = _generate_name(self.__class__.__name__)
        self.entities = {}

    def __repr__(self):
        return f"{self.__class__.__name__}(lead={self.lead}, " \
               f"trail={self.trail}, ordered={self.ordered})"

    def matches(self, message: MessageMixin) -> bool:
        """
        Boolean indicator to whether the command
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
            pyttman.MessageMixin
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

    def truncate_message(self, message: MessageMixin):
        as_set = set(message.lowered_content())
        as_set -= set(self.lead)
        as_set -= set(self.trail)
        return list(as_set)

    def generate_help(self) -> list:
        input_string_parser_fields = self.EntityParser().get_parsers()
        if not self.help_string:
            help_string = f"\n\n> Help section for command '{self.name}'\n" \
                          f"\n\t> Description:\n\t\t{self.description}" \
                          f"\n\t> Syntax:\n\t\t[{'|'.join(self.lead)}]"
            if self.trail:
                help_string += f"[{'|'.join(self.trail)}]\n"

            if input_string_parser_fields:
                help_string += f"\n\t> Entities (information you can provide) :"
                for field_name, parser in input_string_parser_fields.items():
                    help_string += f"\n\t\t * {field_name}"
                    if isinstance(parser, ChoiceParser):
                        help_string += f" - Valid choices: {parser.choices}"
                help_string += "\n"

            if parsers := list(input_string_parser_fields.values()):
                for parser in parsers:
                    if isinstance(parser, ChoiceParser):
                        help_string += ""

            if self.example:
                help_string += f"\n\t> Example:\n\t\t'{self.example}'\n"
        else:
            help_string = self.help_string
        return help_string.splitlines(keepends=True)

    def process(self, message: MessageMixin) -> Reply:
        """
        Iterate over all ValueParser objects and the name
        of the field it's allocated as.
        :param message: MessageMixin object
        :return: Reply, logic defined in the 'respond' method
        """
        entity_parser = self.EntityParser()
        entity_parser.parse_message(message, memoization=self.entities)
        self.entities = entity_parser.value

        try:
            reply: Reply = self.respond(message=message)
        except Exception as e:
            reply = _generate_error_entry(message, e)

        if not reply or not isinstance(reply, Reply):
            raise ValueError(f"Improperly configured Command class: "
                             f"{self.__class__.__name__}."
                             f"respond method returned '{type(reply)}', "
                             f"expected Reply object")

        # Purge entities values and all parser instances from their local values
        self.entities.clear()
        for parser_name in entity_parser.get_parsers():
            parser = getattr(entity_parser, parser_name)
            parser.reset()
        return reply


class Command(BaseCommand):
    def respond(self, message: MessageMixin) -> Reply:
        raise NotImplementedError("The 'respond' method must be "
                                  "defined when subclassing Command")
