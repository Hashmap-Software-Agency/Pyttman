from pyttman.tools.apihandles import RestApiHandle
from pyttman.tools.scheduling.schedule import schedule

from pyttman.tools.pollcache import PollCache
from pyttman.core.interpretation import Interpretation
from pyttman.core.decorators import PyttmanLogger
from pyttman.core.decorators import scheduledmethod
from pyttman.core.internals import _cim, is_dst
from pyttman.core.ability import Ability
from pyttman.core.internals import load_settings

__version__ = '1.1.4'


# Set by the user in each projects' main.py file, imported locally
settings = None
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
