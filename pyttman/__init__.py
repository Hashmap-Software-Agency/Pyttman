from pyttman.tools.apihandles import RestApiHandle
from pyttman.tools.scheduling.schedule import schedule

from pyttman.tools.pollcache import PollCache
from pyttman.core.parsing.commandprocessor import CommandProcessor
from pyttman.core.interpretation import Interpretation
from pyttman.core.decorators import Logger as logger
from pyttman.core.decorators import scheduledmethod
from pyttman.core.internals import _cim, is_dst
from pyttman.core.callback import Callback
from pyttman.core.features import Feature
from pyttman.core.internals import load_settings

__version__ = '1.0.3'

# Set by the user in each projects' main.py file, imported locally
settings = None
is_configured = False

"""
I love you

- That was written by my girlfriend without me knowing about it, 
on that very line. I left my computer unlocked some time during 
a weekend. It's so sweet that I can't remove it, so it's here, 
a part of the framework forever, that's the way it is. Consider 
yourself the founder of an easter egg.

// Simon Olofsson, lead developer and founder of Pyttman

"""
