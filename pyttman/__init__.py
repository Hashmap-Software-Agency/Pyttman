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
