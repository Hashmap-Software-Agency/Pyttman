import sys

import pyttman
from pyttman.clients.base import BaseClient
from pyttman.core.containers import Message, Reply, \
    ReplyStream


class CliClient(BaseClient):
    """
    Very simple CLI - client, offering a user interface
    with pyttman apps through the terminal window.
    """
    def run_client(self):
        print(f"\nPyttman v.{pyttman.__version__} - "
              f"CLI client", end="\n")
        try:
            print(f"{pyttman.settings.APP_NAME} is online! Start chatting"
                  f" with your app below."
                  "\n(?) Use Ctrl-Z or Ctrl-C plus Return to exit",
                  end="\n\n")
            while True:
                message = Message(input("[YOU]: "), client=self)
                reply: Reply | ReplyStream = self.\
                    message_router.get_reply(message)

                if isinstance(reply, ReplyStream):
                    while reply.qsize():
                        print(f"[{pyttman.settings.APP_NAME.upper()}]: ",
                              reply.get().as_str())
                elif isinstance(reply, Reply):
                    print(f"{pyttman.settings.APP_NAME}:", reply.as_str())
                print()
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

    @staticmethod
    def publish(reply: Reply):
        print(reply.as_str())
