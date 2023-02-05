import abc
import random
import warnings
from copy import copy
from typing import List, Any, Iterable

import pyttman
from pyttman.core.exceptions import PyttmanProjectInvalidException
from pyttman.core.entity_parsing.parsers import parse_entities
from pyttman.core.ability import Ability
from pyttman.core.intent import Intent
from pyttman.core.containers import MessageMixin, Reply, ReplyStream, Message
from pyttman.core.internals import _generate_error_entry


class AbstractMessageRouter(abc.ABC):
    """
    Abstract class for a MessageRouter.

    MessageRouters delegate Message objects
    coming from Clients, originating from some
    kind of platform with a user interface.

    Message routers can be very simple and
    linearly search through Abilities and their
    Intent classes and select the first one
    matching - or they can be powered by internal
    caches, learn patterns and be powered by
    Machine learning.

    Users should rarely encounter this class as
    it's being used outside the scope of apps
    developed in Pyttman.
    """

    help_keyword = "help"

    def __init__(self, abilities: List[Ability],
                 intent_unknown_responses: List[str],
                 help_keyword: str, **kwargs):
        self.abilities = abilities
        self.help_keyword = help_keyword
        self.intent_unknown_responses = intent_unknown_responses
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
        :param message: MessageMixin subclassed object, from client
        """
        pass

    @staticmethod
    def process(message: Message,
                intent: Intent,
                keep_alive_on_exc=True) -> Reply | ReplyStream:
        """
        Iterate over all EntityFieldValueParser objects and the name
        of the field it's allocated as.

        The strings present in 'lead' and 'trail' in the Intent are
        filtered out as for them not to be parsed by the Entity parser.

        :param intent: The Intent class chosen to provide a Reply to the user.
        :param message: MessageMixin object
        :param keep_alive_on_exc: Keeps the main loop running if exceptions
        occur in the application logic, and replies with an error message
        fetched from the application settings. Defaults to True.
        :return: Reply, logic defined in the 'respond' method
        """
        joined_patterns = set()

        if intent.exclude_lead_in_entities is True:
            joined_patterns.update(intent.lead)
        if intent.exclude_trail_in_entities is True:
            joined_patterns.update(intent.trail)
        truncated_content = [i for i in message.content
                             if i.casefold() not in joined_patterns]
        truncated_message = Message(content=truncated_content)
        entities: dict[str: Any] = parse_entities(
            message=truncated_message,
            entity_fields=intent.user_entity_fields,
            original_message_content=copy(message.content),
            exclude=intent.ignore_in_entities)

        message.entities = {k: v.value for k, v in entities.items()}

        try:
            intent.before_respond(message)
            reply: Reply | ReplyStream = intent.respond(message=message)
            intent.after_respond(message, reply)
        except Exception as e:
            reply = _generate_error_entry(message, e)
            if keep_alive_on_exc is False:
                raise e

        original_reply = copy(reply)
        try:
            if not any((isinstance(reply, Reply), isinstance(reply, ReplyStream))):
                if isinstance(reply, Iterable) and not isinstance(reply, str):
                    reply = Reply(reply)
                else:
                    reply = ReplyStream(reply)
        except Exception:
            raise PyttmanProjectInvalidException(
                f"Could not return reply from intent '{intent}' due to "
                f"a misconfiguration of the response type. '{intent.respond}' "
                f"returned: '{original_reply}'")

        constraints = {
            bool(reply is not None),
            bool(isinstance(reply, Reply) or isinstance(reply, ReplyStream))
        }

        if False in constraints:
            raise ValueError(f"Improperly configured Intent class: "
                             f"{intent.__class__.__name__}."
                             f"respond method returned '{type(reply)}', "
                             f"expected Reply or ReplyStream")

        for entity_field in intent.user_entity_fields.values():
            entity_field.reset()

        return reply


class FirstMatchingRouter(AbstractMessageRouter):
    """
    Iterates over intents linearly.
    No calculation performed when routing messages and
    multiple abilities matches a Message - the first one
    in order is chosen.
    """

    def get_reply(self, message: Message) -> Reply:
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

        # Return the auto-generated help segment for the Intent if the
        # HELP keyword is the first occurring word in the message.
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
            reply: Reply | ReplyStream = self.process(message=message,
                                                      intent=chosen_intent)
        except Exception as e:
            reply: Reply = _generate_error_entry(message, e)
        return reply

    def get_matching_intent(self, message: MessageMixin) -> List[Intent]:
        """
        Perform a linear search over intents for abilities.
        The matching one first in the sequence is chosen to
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
                    intent = intent(storage=ability.storage,
                                    ability=ability)
                    if intent.matches(message):
                        matching_intents.append(intent)
                except TypeError as e:
                    raise TypeError(f"The intent {intent} did not behave"
                                    f" as expected - see full traceback.") \
                        from e
        return matching_intents
