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

        [setattr(self, k, v) for k, v in kwargs.items()]

        if not self.message_router:
            raise AttributeError("Pyttman Clients require an "
                                 "instance of AbstractMessageRouter "
                                 "subclass for routing messages to "
                                 "Features")

    @abc.abstractmethod
    def run_client(self):
        """
        Starts the main method for the client, opening
        a session to the front end with which it is
        associated with.
        :return: None
        """
        pass
