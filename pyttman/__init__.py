from pyttman import version
from pyttman.tools.scheduling.schedule import schedule
from pyttman.tools.logger.logger import PyttmanLogger

__version__ = version.__version__
__author__ = "Simon Olofsson"
__copyright__ = "(c) Pyttman development Team 2020-2021"
__licence__ = "MIT"


class _SettingsNotConfigured:
    def __getattr__(self, item):
        raise NotImplementedError("pyttman.settings cannot be "
                                  "accessed in this scope. "
                                  "To use pyttman.settings  "
                                  "you must use the Pyttman CLI."
                                  "If you're looking for an "
                                  "interactive shell for debugging, "
                                  "use 'pyttman shell <app name>'. ")


class _AppNotConfigured:
    def __getattr__(self, item):
        raise NotImplementedError("pyttman.app was accessed before its "
                                  "creation. This error can occur if you're "
                                  "trying to decorate functions as lifecycle "
                                  "hooks, in an ability -or intent module, "
                                  "which is included in the 'ABILITIES' list "
                                  "in settings.py. To mitigate this error, "
                                  "move lifecycle hooks to a separate module.")


app = None
settings = _SettingsNotConfigured
is_configured = False
logger = PyttmanLogger

"""
I love you

- That was written by my girlfriend without me knowing about it,
on that very line. I left my computer unlocked some time during
a weekend. It's so sweet that I can't remove it, so it's here,
a part of the framework forever, that's the way it is. Consider
yourself the founder of an easter egg.

// Simon Olofsson, lead developer and founder of Pyttman
"""
