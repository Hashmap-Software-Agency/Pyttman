from dataclasses import dataclass
from datetime import datetime

"""
Details:
    2020-07-05
    
    pyttman framework Message source file

Module details:
    
    The Message object is meant to be a symbolic model
    of how a message could be constructed. Most API's 
    provide the developer with a Message object for this
    purpose, but if you develop your own app, then this
    object is a good container for the recieved command.

    The CommandProcessor object relies on the ".content"
    property of the provided object from the front end,
    so it cannot simply be a string, it needs this property.

    Since pyttman is supposed to be platform and
    API independent, this Message object is used for
    type hinting throughout the framework, and is a good
    contender for when a developer needs a container for 
    their string input that is tested and supported by
    the frameworks all instances.
"""


@dataclass
class Message:
    """
    This class represents a crude structure of
    the message object received, inspired by the message class
    from the the Discord API.

    The intent with this class is to have something
    independet of platform to refer to with the type
    hinting in this framework, as well as providing
    a construct to use if a given platform does not
    provide a message object of this nature from the API.

    The developer can then use the message string and
    assign it to the 'content' property, which the
    CommandProcessor relies on to function normally.
    """
    author: str = None
    content: list = None
    channel: int = None
    created_at: datetime = None
