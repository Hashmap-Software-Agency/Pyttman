import functools
import sys
import random
import traceback

from typing import Tuple

import pytman
from pytman.core.decorators import Logger
from pytman.core.internals import _cim
from pytman.core.interpretation import Interpretation
from pytman.models.message import Message
from pytman.core.bases import Feature

"""
Details:
    2020-07-05
    
    pytman framework ComandProcessor source file

Module details:
    
    The CommandProcessor is the routing object of
    pytman, acting as the main agent that
    will direct messages to Features in the application.
"""


class CommandProcessor:
    """
    This object, while integrated to a front end
    works as a way to parse and understand what a
    human is asking for. An object containing the 
    representation of the interpretation of said
    sentence or word is returned of class 
    Interpretation. 
    """

    # Normally loaded with the project settings.py file

    def __init__(self, **kwargs):
        try:
            self.default_responses = pytman.settings.DEFAULT_RESPONSES
        except AttributeError:
            self.default_responses = None

        self._features = tuple()
        for k, v in kwargs.items():
            setattr(self, k, v)

        if pytman.settings is None:
            raise NotImplementedError(f"{_cim.warn}: Settings are not loaded for "
                                      f"your app. CommandProcessor cannot process "
                                      f"messages unless language and default responses\n"
                                      f"are configured. Use the 'settings.py' file in "
                                      f"the app directory and call 'pytman.load_setings() "
                                      f"in your main.py file for your app,\n"
                                      f"before instantiating a CommandProcessor.\n")

    @property
    def features(self) -> tuple:
        return self._features

    @features.setter
    def features(self, features: Tuple[Feature]):
        if not isinstance(features, tuple):
            self._features = (features,)
        else:
            self._features = features

    def process(self, message: Message) -> Interpretation:
        """
        Splits content field on the Message object, for processing
        in _interpret.
        """
        errors_occurred = False

        if isinstance(message.content, str):
            message.content = message.content.split()

        try:
            return self._interpret(message)
        except Exception as e:
            sys.stderr.write(f"{_cim.err}: Error occured when parsing message: {e} ")
            errors_occurred = True
            raise e
        finally:
            if errors_occurred:
                err_message = str(traceback.format_exc())
                Logger.log(err_message, "error")
                return Interpretation(error=message,
                                      response=lambda: f'Oops! An internal error occurred. '
                                                       f'This occurrence has been logged.',
                                      original_message=tuple(message.content))

    def _interpret(self, message: Message) -> Interpretation:
        """
        Identify the pronouns in the given message. Try to 
        match the pronouns aganst the mapped pronouns property
        for each featrure. If multiple features match the set of
        pronouns, the message is given to each feature for keyword
        matching. The feature that returns a match is given the
        message for further processing and ultimately returning
        the response.
        """

        for feature in self.features:
            if not (return_callable := feature.find_matching_callback(message)):
                continue
            else:
                return Interpretation(feature_name=feature.__class__.__name__,
                                      response=return_callable,
                                      original_message=tuple(message.content))

        language = pytman.settings.CHOSEN_LANGUAGE
        default_responses = self.default_responses[language]["NoResponse"]
        random_response = functools.partial(random.choice, default_responses)

        return Interpretation(feature_name="pytman_builtin",
                              response=random_response,
                              original_message=tuple(message.content))
