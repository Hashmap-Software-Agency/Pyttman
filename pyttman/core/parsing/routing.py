import abc
import random
from typing import List

from pyttman import settings
from pyttman.core.communication.command import Command
from pyttman.core.communication.models.containers import Message, Reply


class AbstractMessageRouter(abc.ABC):
    """
    Abstract class for a MessageRouter.

    The MessageRouter replaces the legacy
    CommandProcessor class.

    It acts as the first instance when relaying
    an incoming message from a front end client,
    passing the message to the correct feature.

    Users should rarely encounter this class as
    it's being used outside the scope of apps
    developed in Pyttman.
    """

    def __init__(self, **kwargs):
        self.features = []
        [setattr(self, k, v) for k, v in kwargs.items()]

    @abc.abstractmethod
    def get_matching_command(self, message: Message) -> List[Command]:
        """
        Return all matching Command classes which match
        a given message, as made evident by their
        lead and trail configuration.

        :param message: Message object, from client
        :return: collection of Commands, if multiple.
        """
        pass

    @abc.abstractmethod
    def get_reply(self, message: Message) -> Reply:
        """
        Return the Reply from matching Command.
        If no command matched, return a response from
        default_responses in settings.

        If the command contains help, return the help
        string for the matching command.
        :return: Reply
        """
        pass


class LinearSearchFirstMatchingRouter(AbstractMessageRouter):
    """
    Iterates over commands linearly.
    No calculation performed when routing messages and
    multiple features matches a Message - the first one
    in order is chosen.
    """

    def get_reply(self, message: Message) -> Reply:
        matching_commands = self.get_matching_command(message)

        if not matching_commands:
            language = settings.CHOSEN_LANGUAGE
            default_responses = settings.DEFAULT_RESPONSES[language]["NoResponse"]
            return Reply(random.choice(default_responses))

        chosen_command = matching_commands[0]
        if "help" in message.content:
            return Reply(chosen_command.generate_help())
        return chosen_command.process(message=message)

    def get_matching_command(self, message: Message) -> List[Command]:
        matching_commands = []
        for feature in self.features:
            for command in feature.commands:
                try:
                    if command.matches(message):
                        matching_commands.append(command)
                except TypeError as e:
                    raise TypeError("It looks like your Command classes are not "
                                    "initialized. Command classes must be initialized "
                                    "when setting them in the class field for "
                                    "a feature, not class references. "
                                    "E.g.: `commands = (FooCommand(), BarCommand())`, "
                                    "and not `commands = (FooCommand, BarCommand)") from e
        return matching_commands
