
from dataclasses import dataclass


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
    value: str
    index_in_message: int

    def __eq__(self, other):
        return other.value == self.value \
               and other.index_in_message == self.index_in_message
