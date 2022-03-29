import inspect
import traceback
import uuid
import warnings
from dataclasses import dataclass
from datetime import datetime

import pytz

import pyttman
from pyttman.core.communication.models.containers import MessageMixin, Reply


def is_dst(timezone: str):
    """
    method for returning a bool whether or not a timezone
    currently is in daylight savings time, useful for servers
    that run systems outside of the user timezone.
    :param timezone:
        string, timezone to give pytz for the dst query.
        look up available timezones at this url:
        https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz
        -timezones
    :returns:
        bool
    """
    timezone = pytz.timezone(timezone)
    timezone_aware_date = timezone.localize(datetime.now(), is_dst=None)
    return timezone_aware_date.tzinfo._dst.seconds != 0


class Settings:
    """
    Dataclass holding settings configured in the settings.py
    settings module. Modules are not picklable in Python,
    thus this class holds the user-level variables and
    objects created in the module instead of the flooding
    of using the entire module as reference in 'pyttman.settings'
    throughout Pyttman apps.

    The Settings class automatically omitts any instance
    in **kwargs being of instance <module> since modules
    aren't picklable. It also omitts functions as callables
    aren't valid settings.
    """
    APPEND_LOG_FILES: bool
    MESSAGE_ROUTER: dict
    ABILITIES: list
    FATAL_EXCEPTION_AUTO_REPLY: list
    CLIENT: dict
    APP_BASE_DIR: str
    LOG_FILE_DIR: str
    APP_NAME: str
    LOG_FORMAT: str
    LOG_TO_STDOUT: bool = False

    def __init__(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items()
         if not inspect.ismodule(v)
         and not inspect.isfunction(v)]

    def __repr__(self):
        _attrs = {name: value for name, value in self.__dict__.items()}
        return f"Settings({_attrs})"


@dataclass
class _cim:
    """
    This class is only used as a namespace
    for internal messages used by exceptions
    or elsewhere by pyttman classes
    and functions. Not for instantiating.
    """
    deprecated_warn: str = "pyttman DEPRECATED WARNING"
    warn: str = "Pyttman WARNING"
    err: str = "Pyttman ERROR"


def load_settings(*args):
    raise DeprecationWarning("The function 'load_settings' is deprecated "
                             "deprecated as of version 1.1.4. Instead of "
                             "manually loading settings in your main.py, "
                             "consider creating a project with pyttman-cli "
                             "and use the clients provided in the framework, "
                             "or create your own by subclassing BaseClient.")


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
    didn't reply back at all.
    :param message: MessageMixin
    :param exc: Exception
    :return: Reply
    """
    error_id = uuid.uuid4()
    traceback.print_exc()
    warnings.warn(f"{datetime.now()} - A critical error occurred in the "
                  f"application logic. Error id: {error_id}")
    pyttman.logger.log(level="error",
                       message=f"CRITICAL ERROR: ERROR ID={error_id} - "
                               f"The error was caught while processing "
                               f"message: '{message}'. Error message: '{exc}'")

    return Reply(f"{pyttman.settings.FATAL_EXCEPTION_AUTO_REPLY} - "
                 f"Error id: {error_id}")


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

    client: Any
    name: str | None = field(default=None)
    settings: Settings | None = field(default=None)
    abilities: set = field(default_factory=set)
    hooks: LifecycleHookRepository = field(
        default_factory=lambda: LifecycleHookRepository())

    def start(self):
        """
        Start a Pyttman application.
        """
        try:
            self.client.run_client()
        except Exception:
            warnings.warn(traceback.format_exc())
