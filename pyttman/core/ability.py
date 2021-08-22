import functools
import inspect
from abc import ABC, abstractmethod
from typing import Optional, Any, Tuple, List

from pyttman.core.callback import Callback
from pyttman.core.communication.intent import Intent
from pyttman.core.communication.models.containers import MessageMixin
from pyttman.core.internals import _generate_name
from pyttman.core.storage.basestorage import Storage


class AbilityABC(ABC):
    """ 
    Represent the template for a complete and 
    ready-to-use ability.
    """

    @abstractmethod
    def find_matching_callback(self, message: MessageMixin) -> bool:
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
        Hook method which runs during the construction
        of a Ability.
        Configure things such as callback bindings (legacy),
        set up the Storage object with data for your intents
        to use, make external calls to a server,
        and other settings. A way to abstract the
        need to overload __init__ and just configure
        instance variables without the overhead
        of calling super() and passing *args and **kwargs.
        @return: None
        """
        pass

    @abstractmethod
    def _get_callback(self, message: MessageMixin) -> Callback:
        """
        << DEPRECATED >>
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


class Ability(AbilityABC):
    """
    Base class for an Ability.

    The Ability is an encapsulating class which
    holds Intent subclasses in its 'intents' tuple.

    It provides an encapsulating scope for Commands
    which shares Storage object. Since this data may
    be sensitive and irrelevant for other functionality
    in the app, this encapsulation provides comfort and
    security for the Intent endpoints not to access or
    destroy data which they're not meant to.

    The Ability class can be configured when used, to
    set up objects in the Storage object, or any other
    code that needs to run before the app starts - can
    be put in or called by the 'configure' method
    """
    description = "Unavailable"
    intents: Tuple = None

    def __init__(self, **kwargs):
        self.storage = Storage()
        self.name = _generate_name(self.__class__.__name__)
        self._callbacks = ()
        self.configure()
        [setattr(self, k, v) for k, v in kwargs]

        if self.intents is not None:
            self.__validate_commands()
        else:
            raise AttributeError(f"Ability {self.__class__.__name__} "
                                 f"has no intents. Provide at least "
                                 f"one Intent class in the 'intents' "
                                 f"property tuple.")

    def find_matching_callback(self, message: MessageMixin) -> \
            Optional[functools.partial]:

        if callback := self._get_callback(message):
            return functools.partial(callback.func, message=message)
        return None

    def __repr__(self):
        return f'Ability({type(self).__name__})'

    def configure(self):
        pass

    def _get_callback(self, message: MessageMixin) -> Optional[Any]:
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

    def __validate_commands(self):
        """
        Assert that the tuple contains references to
        Intent subclasses and nothing else.
        """
        try:
            iter(self.intents)
            if not isinstance(self.intents, Tuple):
                raise TypeError
        except TypeError:
            raise TypeError(f"The 'intents' property must be tuple, got {type(self.intents)}'.")
        else:
            for intent_class in self.intents:
                if not inspect.isclass(intent_class) or not issubclass(intent_class, Intent):
                    raise TypeError(f"Intent '{intent_class}' is not defined correctly. "
                                    f"Intents must be class references, and must inherit "
                                    "from the 'Intent' base class.\nBe sure to only mention "
                                    "the name of the class, and not instantiate it when "
                                    "defining the 'intents' property in your Ability class.\n"
                                    "Hint: Change '(FooIntent(), BarIntent())' to "
                                    "'(FooIntent, BarIntent).")

                # Validate the EntityParser by calling constructor
                try:
                    intent_class().EntityParser()
                except Exception as e:
                    raise AttributeError("An error occurred with the EntityParser "
                                         f"in command {intent_class}: {e}")
