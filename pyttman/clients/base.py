#     MIT License
#
#      Copyright (c) 2021-present Simon Olofsson
#
#      Permission is hereby granted, free of charge, to any person obtaining a copy
#      of this software and associated documentation files (the "Software"), to deal
#      in the Software without restriction, including without limitation the rights
#      to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#      copies of the Software, and to permit persons to whom the Software is
#      furnished to do so, subject to the following conditions:
#
#      The above copyright notice and this permission notice shall be included in all
#      copies or substantial portions of the Software.
#
#      THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#      IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#      FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#      AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#      LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#      OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#      SOFTWARE.

#     MIT License
#
#
#      Permission is hereby granted, free of charge, to any person obtaining a copy
#      of this software and associated documentation files (the "Software"), to deal
#      in the Software without restriction, including without limitation the rights
#      to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#      copies of the Software, and to permit persons to whom the Software is
#      furnished to do so, subject to the following conditions:
#
#
import abc
from pyttman.core.parsing.routing import AbstractMessageRouter


class BaseClient(abc.ABC):
    """
    Baseclass for Clients, for interfacing
    with users directly or through an API.
    """

    def __init__(self, *args, message_router: AbstractMessageRouter, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_router = message_router
        self.name = self.__class__.__name__

        [setattr(self, k, v) for k, v in kwargs.items()]

        if not self.message_router:
            raise AttributeError("Pyttman Clients require an "
                                 "instance of AbstractMessageRouter "
                                 "subclass for routing messages to "
                                 "Intents")

    def __repr__(self):
        return f"{self.name}({vars(self)})"

    @abc.abstractmethod
    def run_client(self):
        """
        Starts the main method for the client, opening
        a session to the front end with which it is
        associated with.
        :return: None
        """
        pass
