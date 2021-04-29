from .tools.apihandles import RestApiHandle
from .tools.scheduling.schedule import schedule

from .tools.pollcache import PollCache
from .core.commandprocessor import CommandProcessor
from .core.interpretation import Interpretation
from .core.decorators import Logger as logger
from .core.decorators import scheduledmethod
from .core.internals import _cim, is_dst
from .core.callback import Callback
from .core.bases import Feature
from .models.message import Message
from .core.internals import load_settings

__version__ = '1.0.0'

# Set by the user in each projects' main.py file, imported locally
settings = None

"""
I love you

- That was written by my girlfriend without me knowing about it, 
on that very line. I left my computer unlocked some time during 
a weekend. It's so sweet that I can't remove it, so it's here, 
a part of the framework forever, that's the way it is. Consider 
yourself the founder of an easter egg.

// Simon Olofsson, lead developer and founder of Pytman

"""
