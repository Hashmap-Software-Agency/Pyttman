import warnings

from pyttman.core.middleware.routing import FirstMatchingRouter
warnings.filterwarnings("default")
warnings.warn(
    "Your settings.py file needs updating."
    "MessageRouter classes were moved with release "
    "1.1.10, in order to expand the Middleware "
    "layer of Pyttman. This import is still working for "
    "compatibility reasons, but will be removed "
    "in further releases. \nTo fix this, change "
    "the import path in settings.py for the router "
    "to the new import path. To find the new import path, "
    "please refer to "        
    "https://github.com/dotchetter/Pyttman/wiki/Middleware",
    DeprecationWarning
)
