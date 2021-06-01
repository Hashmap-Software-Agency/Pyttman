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
    prefixes = None
    suffixes = None

    def parse_message(self, message: Message) -> None:
        """
        If an identifier class is provided,
        the return from the identifier is prioritized
        and returned if it should match an element
        in the message.
        :param message:
        :return:
        """
        if self.identifier is not None:
            if value := self.identifier().get_matching_string(message):
                self.value = value

        if self.prefixes:
            for prefix in self.prefixes:
                try:
                    prefix_index = message.content.index(prefix)
                    value = message.content[prefix_index + 1]
                except ValueError:
                    continue
                else:
                    self.value = value

        elif self.suffixes:
            for suffix in self.suffixes:
                try:
                    prefix_index = message.content.index(suffix)
                    value = message.content[prefix_index - 1]
                except ValueError:
                    continue
                else:
                    self.value = value


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
