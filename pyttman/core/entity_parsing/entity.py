from dataclasses import dataclass
from typing import Any


@dataclass
class Entity:
    """
    The Entity class represents a string value, identified
    in a message object from a user. Entities are strings
    with value of interest. It could be anything from a
    phone number, to the name of a restaurant, or which
    city a weather question relates to.

    The Entity class keeps track of its own occurrence in
    the message object from which it stems, and its string value.
    """
    value: Any
    index_in_message: int = 0
    is_fallback_default: bool = False

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.value

        try:
            return other.value == self.value \
               and other.index_in_message == self.index_in_message
        except AttributeError:
            return False
