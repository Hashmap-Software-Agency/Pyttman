import abc

from pyttman.core.containers import MessageMixin, Reply, ReplyStream
from pyttman.core.middleware.routing import AbstractMessageRouter
from pyttman.core.plugins.base import PyttmanPlugin


class BaseClient(abc.ABC):
    """
    Baseclass for Clients, for interfacing
    with users directly or through an API.
    """
    def __init__(self,
                 message_router: AbstractMessageRouter,
                 plugins: list[PyttmanPlugin],
                 **kwargs):
        self.message_router = message_router
        self.name = self.__class__.__name__
        self.plugins = plugins

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

    def reply_to_message(self, message: MessageMixin) -> Reply | ReplyStream:
        """
        Wrapper for calling the message router for a reply, whilst
        calling plugin methods in order.
        """
        return self.message_router.get_reply(message)
