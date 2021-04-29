from pytman.tools.apihandles import RestApiHandle
from pytman.tools.scheduling.schedule import schedule

from pytman.tools.pollcache import PollCache
from pytman.core.commandprocessor import CommandProcessor
from pytman.core.interpretation import Interpretation
from pytman.core.decorators import Logger as logger
from pytman.core.decorators import scheduledmethod
from pytman.core.internals import _cim, is_dst
from pytman.core.callback import Callback
from pytman.core.bases import Feature
from pytman.models.message import Message
from pytman.core.internals import load_settings

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
