from pyttman.clients.base import BaseClient
from pyttman.core.communication.models.containers import Message


class CliClient(BaseClient):
    def run(self):
        print("Pyttman CLI client\n\nStart chatting with your app below!\n")
        while True:
            message = Message(input("-> "))
            print(self.router.get_reply(message))
