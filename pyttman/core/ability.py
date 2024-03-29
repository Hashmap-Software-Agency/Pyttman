import inspect
from typing import Tuple

from pyttman.core.intent import Intent
from pyttman.core.internals import _generate_name
from pyttman.core.mixins import PrettyReprMixin
from pyttman.core.storage.basestorage import Storage


class Ability(PrettyReprMixin):

    """
    Base class for an Ability.

    The Ability is an encapsulating class which
    holds Intent subclasses in its 'intents' tuple.

    It provides an encapsulating scope for Intents
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

    __repr_fields__ = ("name",)

    def __init__(self, **kwargs):
        super().__init__()

        self.storage = Storage()
        self.name = _generate_name(self.__class__.__name__)
        self.before_create()
        [setattr(self, k, v) for k, v in kwargs.items()]

        if self.intents is not None:
            self.__validate_intents()

    def __validate_intents(self):
        """
        Assert that the tuple contains references to
        'Intent' subclasses and nothing else.
        """
        try:
            iter(self.intents)
            if not isinstance(self.intents, Tuple):
                raise TypeError
        except TypeError:
            raise TypeError(f"The 'intents' property must be tuple, "
                            f"got {type(self.intents)}'.")
        else:
            for intent_class in self.intents:
                if not inspect.isclass(intent_class) or not \
                        issubclass(intent_class, Intent):
                    raise TypeError(
                        f"Intent '{intent_class}' is not defined correctly. "
                        f"Intents must be class references, and must inherit "
                        "from the 'Intent' base class.\nBe sure to only "
                        "mention the name of the class, and not instantiate "
                        "it when defining the 'intents' property in your "
                        "Ability class.\nHint: Change '(FooIntent(), "
                        "BarIntent())' to '(FooIntent, BarIntent).")

    def before_create(self):
        """
        Lifecycle hook. This hook method is executed before the
        ability is created, when the application starts, but it
        does have access to the Storage object.
        """
        pass
