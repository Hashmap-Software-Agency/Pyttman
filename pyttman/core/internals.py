import inspect
import traceback
import uuid
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pyttman
from pyttman.core.containers import MessageMixin, Reply
from pyttman.core.decorators import LifecycleHookRepository
from pyttman.core.exceptions import PyttmanPluginException
from pyttman.core.mixins import PrettyReprMixin
from pyttman.core.plugins.base import PyttmanPlugin


def depr_raise(message: str, version: str) -> None:
    """
    Raise DeprecationWarning with a message and version tag for users.
    :param message: Deprecation message to display to users
    :param version: Pyttman version in which deprecation was declared
    :raise DeprecationWarning
    """
    out = f"{message} - This was deprecated in version {version}."
    raise DeprecationWarning(out)


def depr_graceful(message: str, version: str):
    """
    Uses warnings.warn with a message and version tag for users.
    :param message: Deprecation message to display to users
    :param version: Pyttman version in which deprecation was declared
    """
    out = f"{message} - This was deprecated in version {version}."
    warnings.warn(out, DeprecationWarning)


class Settings:
    """
    Dataclass holding settings configured in the settings.py
    settings module. Modules are not picklable in Python,
    thus this class holds the user-level variables and
    objects created in the module instead of the flooding
    of using the entire module as reference in 'pyttman.settings'
    throughout Pyttman apps.

    The Settings class automatically omits any instance
    in **kwargs being of instance <module> since modules
    aren't picklable. It also omits functions as callables
    aren't valid settings.
    """

    def __init__(self, dictionary=None, **kwargs):
        if dictionary is None:
            dictionary = {}
        self.__dict__.update(dictionary)
        self.APPEND_LOG_FILES: bool = True
        self.ROUTER: dict | None = None
        self.ABILITIES: list | None = None
        self.FATAL_EXCEPTION_AUTO_REPLY: list | None = None
        self.CLIENT: dict | None = None
        self.APP_BASE_DIR: str | None = None
        self.LOG_FILE_DIR: str | None = None
        self.APP_NAME: str | None = None
        self.LOG_FORMAT: str | None = None
        self.LOG_TO_STDOUT: bool = False
        self.STATIC_FILES_DIR: Path | None = None
        self.PLUGINS: list | None = None

        [setattr(self, k, v) for k, v in kwargs.items()
         if not inspect.ismodule(v)
         and not inspect.isfunction(v)]

    def __repr__(self):
        _attrs = {name: value for name, value in self.__dict__.items()}
        return f"Settings({_attrs})"


def _generate_name(name):
    """
    Generates a user-friendly name out of
    Command or Ability class names, by
    inserting spaces in camel cased names
    as well as truncating 'Command' and 'Ability'
    in the names.
    :param name: string, name of a class.
                 hint: Command or Ability subclass
    :return: str, 'SetTimeCommand' -> 'Set Time'
    """
    new_name = ""
    for i in ("Ability", "feature", "Command", "command"):
        name = name.replace(i, "")

    for i, c in enumerate(name):
        if i > 0 and c.isupper():
            new_name += " "
        new_name += c
    return new_name


def _generate_error_entry(message: MessageMixin, exc: BaseException) -> Reply:
    """
    Creates a log entry for critical errors with a UUID bound
    to the log file entry, explaining the error. For the front
    end clients, a Reply object is returned to provide for
    end users who otherwise would experience a chatbot who
    didn't reply at all.
    :param message: MessageMixin
    :param exc: Exception
    :return: Reply
    """
    error_id = uuid.uuid4()
    traceback.print_exc()
    warnings.warn(f"{datetime.now()} - A critical error occurred in the "
                  f"application logic. Error id: {error_id}")
    error_message = (f"CRITICAL ERROR: ERROR ID={error_id} - "
                     f"The error was caught while processing message: "
                     f"'{message}'. Error message: '{exc}'")
    try:
        pyttman.logger.log(level="error", message=error_message)
    except Exception:
        print(error_message)

    try:
        auto_reply = pyttman.settings.MIDDLEWARE['FATAL_EXCEPTION_AUTO_REPLY']
    except Exception:
        auto_reply = "An internal error occurred in the application."
    return Reply(f"{auto_reply} ({error_id})")


@dataclass
class PyttmanApp(PrettyReprMixin):
    """
    The highest point of abstraction for a Pyttman application.
    This class holds the Settings, the Abilities and lifecycle hooks
    for the application, including the Client class used to interface with
    the platform of choice.
    This singleton instance is available through 'from pyttman import app'.
    """
    __repr_fields__ = ("name", "client", "hooks")

    @dataclass
    class LoadedPluginContainer:
        """
        Access point for loaded plugins during the app runtime, e.g:
        `from pyttman import app`
        `my_plugin = app.loaded_plugins.SomePluginName`
        """

        def ingest(self, plugin):
            setattr(self, plugin.__class__.__name__, plugin)

    client: Any
    name: str | None = field(default=None)
    settings: Settings | None = field(default=None)
    hooks: LifecycleHookRepository = field(
        default_factory=lambda: LifecycleHookRepository())
    _abilities: set = field(default_factory=set)
    plugins: list[PyttmanPlugin] = field(default_factory=list)
    loaded_plugins: LoadedPluginContainer = field(default_factory=LoadedPluginContainer)

    def start(self):
        """
        Start a Pyttman application.
        """
        # noinspection PyBroadException
        # Execute plugin hooks
        self.execute_plugins_before_start()
        try:
            self.client.run_client()
        except Exception:
            warnings.warn(traceback.format_exc())
        self.execute_plugins_after_stop()

    @property
    def abilities(self):
        return self._abilities

    @abilities.setter
    def abilities(self, abilities):
        for ability in abilities:
            setattr(self, ability.__class__.__name__, ability)
            self._abilities.add(ability)

    def execute_plugins_before_start(self):
        try:
            for plugin in self.plugins:
                self.loaded_plugins.ingest(plugin)
                plugin.before_app_start(self)
        except Exception as e:
            raise PyttmanPluginException(
                f"The plugin '{plugin.__class__.__name__}' "
                f"caused the boostrap to fail.") from e

    def execute_plugins_after_stop(self):
        for plugin in self.plugins:
            plugin.after_app_stops(self)
