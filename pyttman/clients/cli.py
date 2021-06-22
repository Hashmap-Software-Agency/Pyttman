from pyttman.clients.base import BaseClient
from pyttman.core.communication.models.containers import Message


class CliClient(BaseClient):
    def run_client(self):
        print("\n- Pyttman CLI client\n- Start chatting with your app below!\n")
        while True:
            message = Message(input("-> "))
            print(self.router.get_reply(message).as_str())
