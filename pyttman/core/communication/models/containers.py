import re
from datetime import datetime
from queue import Queue
from typing import List, Iterable
from ordered_set import OrderedSet


class MessageMixin:
    """
    Pyttman MessageMixin, to extend the functionalty
    of existing Message classes provided by 3rd party
    libraries and APIs, to also accommodate for the
    internal requirements of the Message object
    which is expected to fulfill a certain contract
    of attributes and methods for parsing messages.

    The MessageMixin class can be included in multiple
    inheritance when a Message-like class is developed
    for supporting a 3rd party library / API.
    """

    def __init__(self, content=None, **kwargs):
        self.author = "anonymous"
        self.created = datetime.now()
        self.client = None
        self.content = content

        try:
            self.content_with_format = str(content).splitlines(keepends=True)
        except ValueError:
            self.content_with_format = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return f"{self.__class__.__name__}(author=" \
               f"{self.author}, created={self.created}, " \
               f"content={self.content})"

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, val):
        if val is None:
            self._content = ["None"]
        elif isinstance(val, str):
            self._content = val.split()
        elif isinstance(val, list) or isinstance(val, tuple):
            self._content = [str(i) for i in val]
        elif isinstance(val, dict):
            self._content = str(val).split()
        else:
            try:
                self._content = repr(val).split()
            except Exception:
                raise TypeError(f"content cannot be type {type(val)} "
                                f"as it is could not be typecasted to "
                                f"str.")

    def sanitized_content(self, preserve_case=False) -> List[str]:
        """
        Return a sanitized version of the .content property.
        This means that the contents in the message
        are stripped of all symbols while digits are still kept.
        Case is preserved if preserve_case is True.
        :return: list
        """
        out = []
        for i in self.content:
            sanitized = re.sub(r"[^\w\s]", "", i)
            if preserve_case:
                out.append(sanitized)
            else:
                out.append(sanitized.lower())
        return out

    def lowered_content(self) -> List[str]:
        """
        Returns the content of the message case lowered.
        :return: list, str
        """
        return [i.lower() for i in self.content]

    def as_str(self, sanitized: bool = False) -> str:
        """
        Return the 'content' field as joined string
        :param sanitized: Return the content as sanitized_content or not
        :return: str
        """
        if sanitized:
            return " ".join(self.sanitized_content())
        elif self.content_with_format is not None:
            return str().join(self.content_with_format)
        return " ".join(self.content)

    def as_list(self, sanitized: bool = False) -> List:
        """
        Return the 'content' field as list
        :return: list
        """
        if sanitized:
            content = self.sanitized_content()
        else:
            content = self.content

        if isinstance(content, list):
            return content
        elif isinstance(content, str):
            return content.split()

    def remove(self, item):
        """
        Removes element from self.content.
        :return: None
        """
        # noinspection PyBroadException
        try:
            self.content.remove(item)
        except Exception:
            pass

    def contains(self, string: str, case_sensitive: bool = True):
        """
        Evaluates whether or not self.contents
        contains an element.


        :param string: string to be evaluated if self.contents
                       does contain or not.
        :param case_sensitive: Consider the case of all strings
                               in self.content when evaluation is done
        :return: bool, contains or not.
        """
        content_as_set = set(self.content)

        if case_sensitive is False:
            return bool(content_as_set.intersection([string]))
        for elem in content_as_set:
            if elem.casefold() == string.casefold():
                return True
        return bool(len([i.casefold() == string.casefold() for i in content_as_set]))

    def truncate(self, collection: Iterable[str], case_sensitive: bool = True) -> None:
        """
        Remove any occurring element in 'collection' from
        self.content.

        if case_sensitive is False, case is not considered
        and strings with different case are also removed.

        The .content property of the Message is casted in
        an OrderedSet for more efficient calculation of
        common denominators in the collections.
        The OrderedSet structure ensures the message order
        isn't compromised in the process.

        :param collection: Iterable with str elements
        :param case_sensitive:
        :return: None
        """

        # Case sensitivity is True; no need to use casefolding.
        try:
            if case_sensitive is True:
                collection_as_set = OrderedSet(collection)
                casefolded_message = OrderedSet(self.content)
                remainder = casefolded_message - casefolded_message.intersection(collection_as_set)
                self.content = list(remainder)
            # Case sensitivity is False; evaluate the collections with casefolding
            else:
                collection_as_set = OrderedSet([i.casefold() for i in collection])
                casefolded_message = OrderedSet((i.casefold() for i in self.content))
                remainder = casefolded_message - collection_as_set.intersection(casefolded_message)
                for elem in casefolded_message:
                    if elem.casefold() not in remainder:
                        self.content.remove(elem)
        except ValueError:
            # Trying to remove something which is does not exist is not a concern.
            pass


class Message(MessageMixin):
    """
    Standard implementation of the MessageMixin
    class without extending any functionality.
    """
    pass


class Reply(MessageMixin):
    """
    The Reply object is expected to be  returned
    from all Intent subclasses.
    """
    pass


class ReplyStream(Queue):
    """
    The ReplyStream class can be used instead of
    the Reply class, whenever a collection of
    Reply objects are to be returned to the
    user. 
    """

    def __init__(self, collection: Iterable = None):
        super().__init__()
        if collection is not None:
            if isinstance(collection, str):
                self.put(collection)
            else:
                try:
                    iter(collection)
                except Exception:
                    raise AttributeError("'collection' must be iterable")
                else:
                    [self.put(i) for i in collection]

    def get(self, block=True, timeout=None):
        """
        Remove and return an item from the ReplyStream.
        """
        element = self._get()
        return Reply(element) if not isinstance(element, Reply) else element
