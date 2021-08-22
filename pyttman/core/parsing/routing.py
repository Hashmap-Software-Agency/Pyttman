import abc
import random
import warnings
from types import ModuleType
from typing import List, Union

import pyttman
from pyttman.core.communication.command import Command
from pyttman import Ability
from pyttman.core.communication.models.containers import MessageMixin, Reply, ReplyStream
from pyttman.core.internals import _generate_error_entry


class AbstractMessageRouter(abc.ABC):
    """
    Abstract class for a MessageRouter.

    The MessageRouter replaces the legacy
    CommandProcessor class.

    It acts as the first instance when relaying
    an incoming message from a front end client,
    passing the message to the correct Ability.

    Users should rarely encounter this class as
    it's being used outside the scope of apps
    developed in Pyttman.
    """

    help_keyword = "help"

    def __init__(self, features: List[Feature],
                 command_unknonw_responses: List[str],
    def __init__(self, abilities: List[Ability],
                 help_keyword: str, **kwargs):
        self.abilities = abilities
        self.help_keyword = help_keyword
        self.command_unknown_responses = command_unknonw_responses
        [setattr(self, k, v) for k, v in kwargs.items()]

    @abc.abstractmethod
    def get_matching_command(self, message: MessageMixin) -> List[Command]:
        """
        Return all matching Command classes which match
        a given message, as made evident by their
        lead and trail configuration.

        :param message: MessageMixin subclassed object, from client
        :return: collection of Commands, if multiple.
        """
        pass

    @abc.abstractmethod
    def get_reply(self, message: MessageMixin) -> Reply:
        """
        Return the Reply from matching Command.
        If no command matched, return a response from
        default_responses in settings.

        If the command contains help, return the help
        string for the matching command.
        :return: Reply
        """
        pass


class FirstMatchingRouter(AbstractMessageRouter):
    """
    Iterates over commands linearly.
    No calculation performed when routing messages and
    multiple abilities matches a Message - the first one
    in order is chosen.
    """

    def get_reply(self, message: MessageMixin) -> Reply:

        try:
            if not (matching_commands := self.get_matching_command(message)):
                return Reply(random.choice(self.command_unknown_responses))
        except Exception as e:
            return _generate_error_entry(message, e)

        if len(matching_commands) > 1:
            warning_message = "More than one command matched a message. " \
                              "Consider changing the Router class in " \
                              "the settings module for this project if " \
                              "you wish your users to receive a choice " \
                              "of which command to execute in situations " \
                              f"like these. Matching commands: " \
                              f"{matching_commands}"
            warnings.warn(warning_message)
            pyttman.logger.log(warning_message)

        # Take the first matching one and use it to reply to the Message.
        chosen_command = matching_commands.pop()

        # Return the auto-generated help segment for the Command if the HELP keyword
        # is the first occurring word in the message.
        try:
            first_word = message.sanitized_content(preserve_case=False)[0]
        except IndexError:
            pass
        else:
            if first_word == self.help_keyword.lower().strip():
                if chosen_command is not None:
                    return Reply(chosen_command.generate_help())
                # else:
                #  TODO - Return help chapter for feature
        try:
            reply: Union[Reply, ReplyStream] = chosen_command.process(message=message)
        except Exception as e:
            reply: Reply = _generate_error_entry(message, e)
        return reply

    def get_matching_command(self, message: MessageMixin) -> List[Command]:
        """
        Perform a linear search over commands for features.
        The matchinf one first in the sequence is chosen to
        reply the user.

        If more than one Command would match, the user is notified
        with a warning as to investigate the design of their Command
        scheme. It may be wiser to use another MessageRouter class
        which supports multiple match routing.
        :param message:
        :return: List of Command instances which match the command
        """
        matching_commands = []
        for feature in self.features:
            for command in feature.commands:
                try:
                    command = command(feature=feature)
                    if command.matches(message):
                        matching_commands.append(command)
                except TypeError as e:
                    raise TypeError(f"The command {command} did not behave"
                                    f" as expected - see full traceback.") from e
        return matching_commands
