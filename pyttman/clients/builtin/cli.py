import pyttman
from typing import Union
from pyttman.clients.builtin.base import BaseClient
from pyttman.core.communication.models.containers import Message, Reply, ReplyStream


class CliClient(BaseClient):
    """
    Very simple CLI - client, offering a user interface
    with pyttman apps through the terminal window.
    """
    def run_client(self):
        print(f"\nPyttman v.{pyttman.__version__} - "
              f"Command-line interface client\n"
              f"->> {pyttman.settings.APP_NAME} is online! Start chatting"
              f" with your app below.\n")

        while True:
            message = Message(input("You: "), client=self)
            reply: Union[Reply, ReplyStream] = self.message_router.get_reply(message)

            if isinstance(reply, ReplyStream):
                while reply.qsize():
                    print(f"{pyttman.settings.APP_NAME}:", reply.get().as_str())
            elif isinstance(reply, Reply):
                print(f"{pyttman.settings.APP_NAME}:", reply.as_str())
            print()

    @staticmethod
    def publish(reply: Reply):
        print(reply.as_str())
