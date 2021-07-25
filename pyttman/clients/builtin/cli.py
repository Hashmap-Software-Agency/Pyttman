import pyttman
from pyttman.clients.builtin.base import BaseClient
from pyttman.core.communication.models.containers import Message, Reply


class CliClient(BaseClient):
    """
    Very simple CLI - client, offering a user interface
    with pyttman apps through the terminal window.
    """
    def run_client(self):
        print(f"\nPyttman v.{pyttman.__version__} - "
              f"Command-line interface client\nStart chatting"
              f" with your app below!\n\n")
        while True:
            message = Message(input("-> "), client=self)
            print(self.message_router.get_reply(message).as_str())

    @staticmethod
    def publish(reply: Reply):
        print(reply.as_str())
