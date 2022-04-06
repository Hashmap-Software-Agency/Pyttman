import concurrent.futures
import functools
from enum import Enum, auto
from functools import singledispatchmethod

from pyttman.core.exceptions import InvalidPyttmanObjectException
from pyttman.core.mixins import PrettyReprMixin


class LifeCycleHookType(Enum):
    """
    Enum class describing which lifecycle hooks are available
    for use in the Pyttman environment.
    """
    before_start = auto()


class LifecycleHookRepository(PrettyReprMixin):
    """
    Container class, encapsulating lifecycle hooks
    for a certain execution point in the lifetime
    of an application.
    """
    __repr_fields__ = ("repository",)

    def __init__(self):
        self.repository: dict = {k: [] for k in LifeCycleHookType}

    def _add_hook(self, hook_type: LifeCycleHookType, hook: callable):
        """
        Adds a lifecycle hook to the repository for the corresponding list
        under a certain lifecycle hook type.
        :raise InvalidPyttmanObjectException: Raised when an invalid
               LifeCycleHookType is referenced
        """
        try:
            self.repository[hook_type].append(hook)
        except ValueError:
            raise InvalidPyttmanObjectException(
                f"The lifecycle hook '{hook_type}' is not supported."
                f"Valid options are: {[i.name for i in LifeCycleHookType]}")

    @singledispatchmethod
    def run(self, *args, **kwargs):
        """
        Decorator.
        Decorate functions or methods in a Pyttman application to have them
        executed in certain points in time for a Pyttman app lifecycle.
        """
        raise NotImplementedError("Cannot directly invoke dispatch method")

    @run.register
    def _(self, hook_type: LifeCycleHookType, *args, **kwargs) -> callable:
        """
        Offers a decorator accepting the Enum 'LifeCycleHookType'
        to tell when the hook is going to be triggered.
        """
        def decorator(hook: callable):
            partial = functools.partial(hook, *args, **kwargs)
            self._add_hook(hook_type, partial)
        return decorator

    @run.register
    def _(self, hook_type: str, *args, **kwargs) -> callable:
        """
        Offers a decorator accepting strings to define the name
        of the LifeCycleHookType to tell when the hook is going to be
        triggered.
        """
        def decorator(hook: callable):
            hook_enum = None
            try:
                hook_enum = LifeCycleHookType[hook_type]
            except KeyError:
                pass  # self._add_hook will raise InvalidPyttmanObjectException
            partial = functools.partial(hook, *args, **kwargs)
            self._add_hook(hook_enum, partial)
        return decorator

    def trigger(self, hook_type: LifeCycleHookType):
        """
        Trigger all hooks under a certain hook key.
        Hooks are executed concurrently using a thread pool.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            [executor.submit(i) for i in self.repository.get(hook_type)]
