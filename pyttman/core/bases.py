import functools
import sys
from abc import ABC, abstractmethod
from typing import Callable, Optional, Dict, Any, Tuple

from pyttman.core.callback import Callback
from pyttman.core.internals import _cim
from pyttman.models.message import Message

"""
Details:
    2020-06-21
    
    pyttman framework baseclass source file

Module details:
    
    This file contains abstract and base classes for 
    the framework called pyttman. 

    In order for a developer to integrate their software
    with a way to bind certain actions and methods in their
    code, the developer needs a way to follow a set of routines
    that guarantees a seamless integration with the front end
    of the application. This framework provides base classes
    to inherit from with a strict set of rules and methods
    already provided to make it easier for the application 
    to scale, as well as letting developers easily integrate
    their software to the front end with their own interfaces.

    To read instructions and see examples how to use this 
    framework with your application - please read the full
    documentation which can be found in the wiki on GitHub
"""


class FeatureABC(ABC):
    """ 
    Represent the template for a complete and 
    ready-to-use feature. 
    """

    @abstractmethod
    def find_matching_callback(self, message: Message) -> bool:
        """
        Designed to be called upon for returning a
        matching Callback instance which returned
        True on a given message object
        @param message:
        @return: bool
        """
        pass

    @abstractmethod
    def configure(self):
        """
        Configure things such as callback bindings,
        and other settings. A way to abstract the
        need to overload __init__ and just configure
        instance variables without the overhead
        of calling super() and passing *args and **kwargs.
        @return: None
        """
        pass

    @abstractmethod
    def _get_callback(self, message: Message) -> Callback:
        """
        Returns the method (function object) bound to a
        Callback object, if eligible. This method
        should be overloaded if a different return behavior
        in a no-match-found scenario is desired.
        @return: Callback
        """
        pass

    @property
    @abstractmethod
    def callbacks(self) -> Tuple[Callback]:
        pass

    @callbacks.setter
    @abstractmethod
    def callbacks(self, callbacks: tuple):
        pass


class Feature(FeatureABC):
    """
    Base class for features.
    There's no need for users to inherit from
    this base class, as the subclass 'Feature'
    in pyttman.models subclasses Feature,
    and can be extended further.
    """

    def __init__(self):
        self.name = None
        self._callbacks = ()
        self.configure()

    def find_matching_callback(self, message: Message) -> \
            Optional[functools.partial]:

        if callback := self._get_callback(message):
            return functools.partial(callback.func, message=message)
        return None

    def __repr__(self):
        if self.name:
            return f'Feature(Feature{self.name})'
        return f'Feature({type(self).__name__})'

    def configure(self):
        pass

    def _get_callback(self, message: Message) -> Optional[Any]:
        for callback in self.callbacks:
            if callback.matches(message):
                return callback
        return None

    @property
    def callbacks(self) -> Tuple[Callback]:
        # noinspection PyTypeChecker
        return self._callbacks

    @callbacks.setter
    def callbacks(self, callbacks: tuple):
        if isinstance(callbacks, dict):
            raise DeprecationWarning(f"callbacks must be of type Callback")

        try:
            iter(callbacks)
        except TypeError:
            callbacks = (callbacks,)
        self._callbacks = callbacks
