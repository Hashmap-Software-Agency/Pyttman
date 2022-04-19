
import abc
from abc import ABC
from collections import OrderedDict
from itertools import zip_longest

from pyttman.core.entity_parsing.parsers import Parser
from pyttman.core.internals import _generate_name, depr_graceful
from pyttman.core.mixins import PrettyReprMixin
from pyttman.core.storage.basestorage import Storage
from pyttman.core.containers import (
    Reply,
    ReplyStream,
    Message
)


class AbstractIntent(abc.ABC):

    @abc.abstractmethod
    def __repr__(self):
        pass

    def respond(self, message: Message) -> Reply | ReplyStream:
        """
        Subclasses overload this method to respond
        to a given Intent upon a match.

        The Intent class is meant to be stateless.
        For replies that require context such as
        cache or other things related to other
        data, the use of the Storage object in the
        Intent instance is encouraged inside this
        method to store and retrieve information.
        """
        pass

    @abc.abstractmethod
    def matches(self, message: Message) -> bool:
        """
        Determine whether a MessageMixin matches an
        Intent instance's pattern config.
        The 'lead' and 'trail'

        Fields are traversed over and sought
        for matching strings.
        :param message: pyttman.MessageMixin object
        :return: bool, Intent matches or not
        """
        pass

    @abc.abstractmethod
    def _assert_ordered(self, message: list) -> bool:
        """
        Tells whether the Message content complies
        with the configuration of 'lead' and 'trail',
        thus meaning that all words defined in 'lead'
        and 'trail' shall occur in the same order in
        the message form the user, as they do in the
        'lead' and 'trail' tuples.
        :param message: Message object, from client
        :return: bool, message is ordered or not
        """

    @abc.abstractmethod
    def generate_help(self):
        """
        Generates a descriptive help_string message based
        on the docstring for the Intent class the
        subclass has defined, as well as including
        the syntax for the Intent using the lead
        and trail fields.

        if the help_string is already defined, this
        help is used and no automated help is
        generated.
        :return:
        """
        pass


class BaseIntent(AbstractIntent, ABC, PrettyReprMixin):
    """
    Base class for an Intent, containing configuration
    on which criteria are set for a message to match
    it, as well as methods to make understanding and
    retrieving data from a message easier.

    The Intent class is similar to an endpoint method
    in MVC, where it will receive a Message object
    upon a matching route given by the MessageRouter,
    much like endpoint methods receive Request objects.

    :field lead:
        Define single strings or a sequence of strings in
        the 'lead' tuple, to define which words shall
        occur in the message for it to match on the
        Intent instance. Selection is  'any of'.

    :field trail:
        Optional: define the 'trail' tuple.
        Similar to the 'lead' tuple - define a single, or
        a sequence of strings which will dictate which
        messages match the Intent. All strings defined
        in the 'trail' tuple must occur AFTER all strings
        defined in 'lead', for the Intent to match.
        This is useful to steer things such as 'search'
        as a lead keyword, in to the right Intent for
        the right 'search'. You may have one Intent
        for 'search for movies' and another for
        'search for the best coffee', in your app.

    :field ordered:
        Remember that all strings in 'lead' and 'trail'
        are 'any of'? That also means that Pyttman will not
        consider their order of appearance left- to right
        in the message compared to your lead and trail
        tuples. This can be set however with the 'ordered'
        parameter, to True. This will require that all
        strings defined in lead and trail, occur in the
        same order as you have defined them

    :field help_string:
        An optional help string which will override the
        auto-generated string that Pyttman builds for
        the user at run time.

    :field description:
        A human friendly piece of text to describe
        what your Intent does.

    :field example:
        Provide your users with an example of how
        a message for this Intent could look.
    """
    __repr_fields__ = ("name", "lead", "trail")

    ability = None
    description: str = "Unavailable"
    example: str = None
    lead: tuple[str] = None
    trail: tuple[str] = None
    ordered: bool = False
    help_string: str = None
    storage: Storage = None
    ignore_in_entities: tuple[str] = None
    exclude_lead_in_entities: bool = True
    exclude_trail_in_entities: bool = True

    def __init__(self, **kwargs):

        [setattr(self, k, v) for k, v in kwargs.items()]

        for attr in ("lead", "trail", "ignore_in_entities"):
            if getattr(self, attr) is None:
                setattr(self, attr, tuple())

        self.user_defined_entity_fields = OrderedDict()
        self.name = _generate_name(self.__class__.__name__)
        self.lead = tuple([i.lower() for i in self.lead])
        self.trail = tuple([i.lower() for i in self.trail])

        entity_field_search_area_dict = self.__class__.__dict__
        if hasattr(self, "EntityParser"):
            depr_graceful("EntityParser classes are redundant since 1.2.0. "
                          "You can declare EntityField´s in the Intent "
                          "without the use of an EntityParser inner class.\n"
                          "using an EntityParser will be deprecated in "
                          "future releases.")
            entity_parser_cls = getattr(self, "EntityParser")
            entity_field_search_area_dict |= \
                entity_parser_cls.__class__.__dict__

        for attr_name, attr_value in entity_field_search_area_dict.items():
            if not any((attr_name.startswith("_"), attr_name.endswith("_"))):
                if issubclass(attr_value.__class__, Parser):
                    self.user_defined_entity_fields[attr_name] = attr_value

    def __repr__(self):
        return f"{self.__class__.__name__}(lead={self.lead}, " \
               f"trail={self.trail}, ordered={self.ordered})"

    def matches(self, message: Message) -> bool:
        """
        Boolean indicator to whether the Intent
        matches a given message, without returning
        the function itself as with the Parse method.

        To begin with, the message has to match at least
        one word in the self.lead property. This is asserted
        through the .intersection method, as to get the word(s)
        that matches the self.lead property in a subset.
        Next, the optional self.trail property is investigated
        similarly if it is defined - otherwise not.

        The self.trail string / collection of strings has to,
        by definition, appear delay the words in self.lead.
        This is asserted by first identifying the words that
        match the trail in the message. The words that also
        are present in the lead are removed by subtraction.
        Next, by iterating over the two collections the order
        of appearance can now be determined by identifying
        the index of the word compared between the two. If
        the index is higher in the trail than the lead, the
        loop continues and will eventually exhaust.
        If not, the trail condition is not met and method
        exits with False.

        :param message:
            pyttman.MessageMixin
        :returns:
            Bool, True if self matches Intent
        """

        match_trail = False
        sanitized = message.as_list(sanitized=True)

        if not (match_lead := [i for i in self.lead if i in sanitized]):
            return False
        elif self.ordered and not self._assert_ordered(sanitized):
            return False

        if self.trail:
            latest_lead_occurrence, latest_trail_occurrence = 0, 0

            if not (match_trail := [i for i in self.trail if i in sanitized]):
                return False

            for lead, trail in zip_longest(match_lead, match_trail):
                try:
                    _index = sanitized.index(lead)
                    if _index > latest_lead_occurrence:
                        latest_lead_occurrence = _index
                except ValueError:
                    pass
                try:
                    _index = sanitized.index(trail)
                    if _index > latest_trail_occurrence:
                        latest_trail_occurrence = _index
                except ValueError:
                    pass
            match_trail = (latest_trail_occurrence > latest_lead_occurrence)
        return match_lead and match_trail or match_lead and not self.trail

    def _assert_ordered(self, message: list) -> bool:
        ordered_trail, ordered_lead = True, True
        for word_a, word_b in zip([i for i in message if i in self.lead],
                                  self.lead):
            if word_a != word_b:
                ordered_lead = False
                break
        if not self.trail:
            return ordered_lead

        for word_a, word_b in zip([i for i in message if i in self.trail],
                                  self.trail):
            if word_a != word_b:
                ordered_trail = False
                break
        return ordered_trail and ordered_lead

    def generate_help(self) -> str:
        #  TODO - Extract
        pass

    def before_respond(self, message: Message) -> None:
        """
        Implement this method to execute code before an Intent starts
        and goes online to users.
        """
        pass

    def after_respond(self, message: Message, reply: Reply) -> None:
        """
        Implement this method to execute code before the App starts
        and goes online to users.
        """
        pass


if __name__ != "__main__":
    Intent = BaseIntent
