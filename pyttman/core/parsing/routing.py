import abc
import random
import warnings
from typing import List, Union

import pyttman
from pyttman import Ability
from pyttman.core.communication.intent import Intent
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
    def get_matching_intent(self, message: MessageMixin) -> List[Intent]:
        """
        Return all matching Intent classes which match
        a given message, as made evident by their
        lead and trail configuration.

        :param message: MessageMixin subclassed object, from client
        :return: collection of Intents, if multiple.
        """
        pass

    @abc.abstractmethod
    def get_reply(self, message: MessageMixin) -> Reply:
        """
        Return the Reply from matching Intent.
        If no command matched, return a response from
        default_responses in settings.

        If the command contains help, return the help
        string for the matching command.
        :return: Reply
        """
        pass


class FirstMatchingRouter(AbstractMessageRouter):
    """
    Iterates over intents linearly.
    No calculation performed when routing messages and
    multiple abilities matches a Message - the first one
    in order is chosen.
    """

    def get_reply(self, message: MessageMixin) -> Reply:

        try:
            if not (matching_intents := self.get_matching_intent(message)):
                return Reply(random.choice(self.intent_unknown_responses))
        except Exception as e:
            return _generate_error_entry(message, e)

        if len(matching_intents) > 1:
            warning_message = "More than one Intent matched a message. " \
                              "Consider changing the Router class in " \
                              "the settings module for this project if " \
                              "you wish your users to receive a choice " \
                              "of which command to execute in situations " \
                              f"like these. Matching intents: " \
                              f"{matching_intents}"
            warnings.warn(warning_message)
            pyttman.logger.log(warning_message)

        # Take the first matching one and use it to reply to the Message.
        chosen_intent = matching_intents.pop()

        # Return the auto-generated help segment for the Intent if the HELP keyword
        # is the first occurring word in the message.
        try:
            first_word = message.sanitized_content(preserve_case=False)[0]
        except IndexError:
            pass
        else:
            if first_word == self.help_keyword.lower().strip():
                if chosen_intent is not None:
                    return Reply(chosen_intent.generate_help())
                # else:
                #  TODO - Return help chapter for ability
        try:
            reply: Union[Reply, ReplyStream] = chosen_intent.process(message=message)
        except Exception as e:
            reply: Reply = _generate_error_entry(message, e)
        return reply

    def get_matching_intent(self, message: MessageMixin) -> List[Intent]:
        """
        Perform a linear search over intents for abilities.
        The matchinf one first in the sequence is chosen to
        reply the user.

        If more than one Intent would match, the user is notified
        with a warning as to investigate the design of their Intent
        scheme. It may be wiser to use another MessageRouter class
        which supports multiple match routing.
        :param message:
        :return: List of Intent instances which match the intent
        """
        matching_intents = []
        for ability in self.abilities:
            for intent in ability.intents:
                try:
                    intent = intent(ability=ability)
                    if intent.matches(message):
                        matching_intents.append(intent)
                except TypeError as e:
                    raise TypeError(f"The intent {intent} did not behave"
                                    f" as expected - see full traceback.") from e
        return matching_intents
