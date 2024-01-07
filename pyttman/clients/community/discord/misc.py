import discord
from pyttman.core.containers import MessageMixin


class DiscordMessage(MessageMixin, discord.Message):
    """
    Message class inheriting both from Pyttman's Message
    object which has methods and mechanics the internals
    of the Pyttman framework depend on, while also
    supporting the Discord module and API for interacting
    with its API to support full interaction with the
    discord platform from within applications developed
    in Pyttman, and not just the content of the message.

    This class is designed to be used with the DiscordClient
    class.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
