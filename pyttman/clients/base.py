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

    def execute_plugins(self,
                        intercept_point: PluginIntercept,
                        payload: MessageMixin):
        """
        Executes plugin methods.
        """
        for plugin in self.plugins:
            if intercept_point is self.PluginIntercept.before_intents:
                plugin.before_intent(payload)
            elif intercept_point is self.PluginIntercept.after_intents:
                plugin.after_intent(payload)
            elif intercept_point is self.PluginIntercept.before_app:
                plugin.before_app_start(pyttman.app)
            elif intercept_point is self.PluginIntercept.after_app:
                plugin.after_app_stops(pyttman.app)

    def reply_to_message(self, message: MessageMixin) -> Reply | ReplyStream:
        """
        Wrapper for calling the message router for a reply, whilst
        calling plugin methods in order.
        """
        self.execute_plugins(intercept_point=self.PluginIntercept.before_intents,
                             payload=message)
        reply = self.message_router.get_reply(message)
        self.execute_plugins(intercept_point=self.PluginIntercept.after_intents,
                             payload=message)
        return reply
