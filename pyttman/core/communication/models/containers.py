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

    def as_str(self) -> str:
        """
        return the 'content' field as joined string
        :return: str
        """
        return " ".join(self.content)

    def as_list(self) -> List:
        """
        return the 'content' field as list
        :return: list
        """
        if isinstance(self.content, list):
            return self.content
        elif isinstance(self.content, str):
            return self.content.split()


class Reply(Message):
    pass
