import re
from datetime import datetime
from typing import List


class Message:

    def __init__(self, content="", **kwargs):
        self.sender = None
        self.author = "anonymous"
        self.created = datetime.now()
        self._content = content

        for k, v in kwargs.items():
            setattr(self, k, v)

        if isinstance(self.content, str):
            self.content = self.content.split()

    def __repr__(self):
        return f"{self.__class__.__name__}(sender=" \
               f"{self.sender}, created={self.created}, " \
               f"content={self.content})"

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, val):
        if isinstance(val, str):
            self._content = val.split()
        elif isinstance(val, list) or isinstance(val, tuple):
            self._content = val
        else:
            raise TypeError(f"Reply.content cannot be type {type(val)},"
                            f"allowed types: [str, tuple, list]")

    def sanitize(self) -> List[str]:
        """
        Return a sanitized version of the .content property.
        This means that the contents in the message
        are stripped of all symbols while case and
        digits are still kept.
        :return: list
        """
        out = []
        for i in self.content:
            out.append(re.sub(r"[^\w\s]", "", i).lower())
        return out

    def as_str(self, sanitized: bool = False) -> str:
        """
        Return the 'content' field as joined string
        :param sanitized: Return the content as sanitized or not
        :return: str
        """
        if sanitized:
            return " ".join(self.sanitize())
        return " ".join(self.content)

    def as_list(self, sanitized: bool = False) -> List:
        """
        Return the 'content' field as list
        :return: list
        """
        if sanitized:
            content = self.sanitize()
        else:
            content = self.content

        if isinstance(content, list):
            return content
        elif isinstance(content, str):
            return content.split()


class Reply(Message):
    pass
