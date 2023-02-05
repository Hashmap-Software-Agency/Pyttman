import sys

import pyttman
from pyttman.clients.base import BaseClient
from pyttman.core.containers import Message, Reply, \
    ReplyStream


class ScriptClient(BaseClient):
    """
    The ScriptClient runs a single file within a Pyttman app
    context.
    This client is suitable for applications which don't have
    a program loop, but are designed to be executed as a script
    to run once.
    """
    def run_client(self, *args, **kwargs):
        print(f"\nPyttman v.{pyttman.__version__} - "
              f"Script client", end="\n")
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
