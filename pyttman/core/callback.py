from itertools import zip_longest
from pyttman.models.message import Message

"""
Details:
    2020-07-17
    
    pyttman framework source file with Callback
    objects

    This module contains objects that are designed to make
    creating callbacks in Features easier, by offering an
    api. 
"""


class Callback:
    """
    Callback class
    The Callback object is a binding between a single
    or a series of words to a method. It's designed to
    be used with the CommandParser object inside a
    Feature object, where the binding between words or
    sequence of words are established.

    It enables developers to quickly and easily create
    callback bindings that automate the structure delay
    instantiation.

    lead:
        (tuple) words in sequence
    trail:
        (tuple) words in sequence, that must be present
        delay words in the _lead tuple
    func:
        method / function / callable that will execute
        if binding matches command
    ordered:
        (bool) whether the order of items in the
        lead or trail property is trivial or not
    """
    IGNORED_CHARS = '?=)(/&%¤#"!,.-;:_^*`´><|'

    __slots__ = ('_lead', '_trail', '_func', '_bindings',
                 '_interactive', '_ordered', '_intact_lead',
                 '_intact_trail')

    def __init__(self, func, lead, trail=None, ordered=False):
        self.bindings = dict()
        self.func = func
        self.lead = lead
        self.trail = trail
        self.ordered = ordered

    def __repr__(self):
        return f"Callback Object(lead: {self._lead}, " \
               f"trail: {self._trail}, func: {self._func})"

    def matches(self, message: Message) -> bool:
        """
        Boolean indicator to whether the callback
        matches a given message, without returning
        the function itself as with the .Parse method.

        Return the callable bound to the Callback instance
        if the message matches the subset(s) of strings
        defined in this object.

        To begin with, the message has to match at least
        one word in the self.lead property. This is asserted
        through the .intersection method, as to get the word(s)
        that matches the self.lead property in a subset.
        Next, the optional self.trail property is investigated
        similarly if it is defined - otherwise not.

        The self.trail string / collection of strings has to,
        by definition, appear delay the words in self.lead.
        This is asserted by first identifying the words that
        matches the trail in the message. The words that also
        are present in the lead are removed by subtraction.
        Next, by iterating over the two collections the order
        of appearence can now be determined by identifying
        the index of the word compared between the two. If
        the index is higher in the trail than the lead, the
        loop continues and will eventually exhaust.
        If not, the trail condition is not met and method
        exits with False.

        :param message:
            pyttman.Message
        :returns:
            Bool, True if self matches command
        """

        match_trail = False

        lowered = [i.lower().strip(Callback.IGNORED_CHARS)
                   for i in message.content]

        if not (match_lead := [i for i in self._lead if i in lowered]):
            return None
        elif self._ordered and not self._assert_ordered(lowered):
            return None

        if self._trail:
            latest_lead_occurence, latest_trail_occurence = 0, 0

            if not (match_trail := [i for i in self._trail if i in lowered]):
                return None

            for lead, trail in zip_longest(match_lead, match_trail):
                try:
                    _index = lowered.index(lead)
                    if _index > latest_lead_occurence:
                        latest_lead_occurence = _index
                except ValueError:
                    pass
                try:
                    _index = lowered.index(trail)
                    if _index > latest_trail_occurence:
                        latest_trail_occurence = _index
                except ValueError:
                    pass
            match_trail = (latest_trail_occurence > latest_lead_occurence)
        return match_lead and match_trail or match_lead and not self._trail

    def _assert_ordered(self, message: list) -> bool:
        ordered_trail, ordered_lead = True, True
        for word_a, word_b in zip([i for i in message if i in self._lead], self._lead):
            if word_a != word_b:
                ordered_lead = False
                break
        if not self._trail:
            return ordered_lead

        for word_a, word_b in zip([i for i in message if i in self._trail], self._trail):
            if word_a != word_b:
                ordered_trail = False
                break
        return ordered_trail and ordered_lead

    @property
    def bindings(self) -> dict:
        return self._bindings

    @bindings.setter
    def bindings(self, bindings: dict):
        self._bindings = bindings

    @property
    def lead(self) -> tuple:
        return self._lead

    @lead.setter
    def lead(self, lead: tuple):
        if isinstance(lead, str): lead = (lead,)
        try:
            for i in lead: self._bindings[i.lower()] = self._func
        except TypeError:
            raise AttributeError("Callback: items in 'lead' and "
                                 "'trail' must be str")
        self._lead = lead

    @property
    def trail(self) -> tuple:
        return self._trail

    @trail.setter
    def trail(self, trail: tuple):
        if trail is None:
            self._trail = None
            return
        if isinstance(trail, str):
            trail = (trail,)

        if collision := [i.lower() for i in self._lead if i in trail]:
            raise AttributeError(f"trail illogical - reoccuring "
                                 f"string from lead: '{collision.pop()}'")

        try:
            for i in trail:
                self._bindings[i.lower()] = self._func
        except TypeError:
            raise AttributeError("Callback: items in 'lead' and "
                                 "'trail' must be str")
        self._trail = trail

    @property
    def func(self) -> callable:
        return self._func

    @func.setter
    def func(self, func: callable):
        if not callable(func):
            raise AttributeError(f"{func} cannot be used as func "
                                 f"parameter as it is not callable")
        self._func = func

    @property
    def ordered(self) -> bool:
        return self._ordered

    @ordered.setter
    def ordered(self, ordered: bool):
        self._ordered = ordered
