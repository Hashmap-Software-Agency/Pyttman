import discord
from pyttman.core.communication.models.containers import Message


class DiscordClient(discord.Client):
    """
    Client class for the Discord chat service.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = ""
        self.guild = ""

        [setattr(self, k, v) for k, v in kwargs.items()]

        if not self.token or not self.guild:
            raise ValueError("Cannot connect - missing authentication."
                             "'token' and 'guild' must be provided when "
                             "using the Discord client.'")

    async def on_message(self, message: discord.Message):
        internal_message = Message()
        for i
            print(self.router.get_reply(message).as_str())

    def run_client(self):
        self.run(self.token)


        # TODO - Figure out a way to pass credentials to the client.
        # TODO - How can the pyttman.Message object be used here?