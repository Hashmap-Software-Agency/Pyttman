import sys

from pyttman.clients.builtin.base import BaseClient
from pyttman.core.communication.models.containers import Message


class CliClient(BaseClient):
    def run_client(self):
        print("\nPyttman CLI client\nStart chatting with your app below!\n")
        while True:
            message = Message(input("-> "),
                              client=self)
            print(self.message_router.get_reply(message).as_str())
