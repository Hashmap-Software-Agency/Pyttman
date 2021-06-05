"""
    This module contains parser objects used
    through out the Pyttman framework.

    Parsers are seen interacting with the
    Command class as a configuration class
    to both identify which command matches
    a message, but also in ValueParser
    classes to add functionality for Command
    classes to identify values behind querystring
    commands which may be a value provider for a command.
"""
import abc

from pyttman.core.communication.models.containers import Message


class AbstractParser(abc.ABC):
    """
    Abstract Parser class
    """

    @abc.abstractmethod
    def parse_message(self, message: Message) -> None:
        pass


class Parser(AbstractParser):
    """
    Base parser,
    Subclass this class when creating a
    custom Parser.
    """
    first_item = 0
    last_item = -1

    identifier = None
    value = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value}," \
               f"identifier={self.identifier})"

    def parse_message(self, message: Message) -> None:
        """
        Parse the message and identify the value
        looked for in the content.
        :return: None
        """
        pass


class ValueParser(Parser):
    """
    Configuration class designed to be defined
    in a Command.ValueParser, as a way to identify
    values behind certain strings.

    Subclasses can add verbosity and define custom
    rules for how query string values are isolated
    and stored.
    """
    identifier = None
    prefixes = tuple()
    suffixes = tuple()

    def parse_message(self, message: Message) -> None:
        """
        If an identifier class is provided,
        the return from the identifier is prioritized
        and returned if it should match an element
        in the message.
        :param message:
        :return:
        """
        identifier_value = None
        prefix_value = None
        suffix_value = None

        # If all criterias are defined, ensure that the Identifier value
        # satisfies the prefixes and/or suffixes strings
        if self.identifier:
            if not (identifier_value := self.identifier().get_matching_string(message)):
                return
            else:
                identifier_index = message.content.index(identifier_value)

            # Make sure the identified value, if any, occurs after all prefixes
            if self.prefixes:
                for prefix in self.prefixes:
                    if prefix in message.content:
                        prefix_index = message.content.index(prefix)
                        if not prefix_index < identifier_index:
                            return
                    else:
                        return

            # Make sure the identified value, if any, occurs before all suffixes
            if self.suffixes:
                for suffix in self.suffixes:
                    if suffix in message.content:
                        suffix_index = message.content.index(suffix)
                        if not suffix_index > identifier_index:
                            return
                    else:
                        return

        else:
            for prefix in self.prefixes:
                try:
                    prefix_index = message.content.index(prefix)
                    prefix_value = message.content[prefix_index + 1]
                except ValueError:
                    continue

            for suffix in self.suffixes:
                try:
                    suffix_index = message.content.index(suffix)
                    suffix_value = message.content[suffix_index - 1]
                except ValueError:
                    continue

        """
        If an identifier is specified without prefix and suffix, its value is
        saved as the ultimate value. 
        
        If suffixes or prefixes or both are also defined, these must occur before
        and after the identifiers value, respectively.
        
        If suffix and prefix are defined together, they should be pointing to the 
        same string, which is only logical. If so, that value is set as the ultimate
        value. 
        
        If suffix or prefix are alone, their first encountered value is set as the
        ultimate value.
        """
        if (self.suffixes and self.prefixes) and not \
                self.identifier and (prefix_value == suffix_value):
            self.value = prefix_value
        elif (self.identifier and self.prefixes) or (self.identifier and self.suffixes):
            self.value = identifier_value
        elif self.prefixes and not self.suffixes:
            self.value = prefix_value
        elif self.suffixes and not self.prefixes:
            self.value = suffix_value
        elif self.identifier and not self.prefixes and not self.suffixes:
            self.value = identifier_value


class PositionalParser(Parser):
    position = Parser.last_item

    def parse_message(self, message: Message) -> None:
        """
        Set whichever element at index 'position'
        as value.
        :param message:
        :return:
        """
        try:
            self.value = message.content[self.position]
        except IndexError:
            pass
