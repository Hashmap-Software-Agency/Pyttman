import abc
from pyttman.core.middleware.routing import AbstractMessageRouter


class BaseClient(abc.ABC):
    """
    Baseclass for Clients, for interfacing
    with users directly or through an API.
    """

    def __init__(self, *args, message_router: AbstractMessageRouter, **kwargs):
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
    def run_client(self, *args, **kwargs) -> None:
        """
        Starts the main method for the client, opening
        a session to the front end with which it is
        associated with.
        """
        pass
