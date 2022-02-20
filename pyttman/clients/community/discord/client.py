
import asyncio
from datetime import datetime

import discord
from typing import Union
from pyttman.clients.base import BaseClient
from pyttman.clients.community.discord.misc import DiscordMessage
from pyttman.core.communication.models.containers import Reply, ReplyStream
from pyttman.core.internals import _generate_error_entry


class DiscordClient(discord.Client, BaseClient):
    """
    Client class for the Discord chat service.
    Token and guild are both required.

    It implements the 'on_message' method overloaded
    from `discord.Client.on_message` , and plugging it
    in to the Pyttman ecosystem, allowing the application
    logic to take care of responding to the message.

    Since the `discord.Client` class provides an
    impressive array of functionality, this class
    can be subclassed by users who wish to implement
    behavior for their application upon any of the
    other available event triggers from the discord.Client
    class, available to read in their documentation.

    Below are attributes and methods unique to the
    `DiscordClient` class.

    Attributes
    -----------
    token: :class:`str`
        Token used when authenticating with Discord's API.
        The token is deleted from the instance at time of
        connection.
    guild: :class:´str`
        Guild ID from Discord, in which the Bot is registered
        to and is allowed to connect to.
    message_startswith: :class:`str`
        Optional string, setting a condition for all messages
        being required to start with said string, for the bot
        to consider the message as a command to parse.
        Defaults to empty string, allowing all messages to
        be parsed.
    message_endswith: :class:`str`
        Optional string, setting a condition for all messages
        being required to end with said string, for the bot
        to consider the message as a command to parse.
        Defaults to empty string, allowing all messages to
        be parsed.
    """
    token: str = ""
    guild: str = ""
    message_startswith: str = ""
    message_endswith: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [setattr(self, k, v) for k, v in kwargs.items()]

    async def on_message(self, message: DiscordMessage) -> None:
        """
        Overloads on_message in discord.Client().The
        method is called implicitly whenever an incoming
        message over the discord interface is intercepted.
        All messages are parsed, thus it's a good idea to
        verify that the author is not self to prevent endless
        loops.
        :param message: discord.Message
        :return: None
        """
        if message.author == self.user:
            return

        # Add the client to the attributes, passed on to the message object
        attrs = {"created": datetime.now(), "client": self}

        for attr_name in message.__slots__:
            try:
                attrs[attr_name] = getattr(message, attr_name)
            except AttributeError:
                # It was likely a method - skip it
                continue

        # Accessing the protected _state field is unfortunately necessary here
        discord_message = DiscordMessage(state=attrs.get("_state"),
                                         data=attrs, **attrs)

        msg_as_str: str = discord_message.as_str()
        if self.message_startswith and not msg_as_str.startswith(
                self.message_startswith) \
                or self.message_endswith and not msg_as_str.endswith(
                self.message_endswith):
            return

        reply: Reply | ReplyStream = self.message_router.get_reply(
            discord_message)
        try:
            if isinstance(reply, ReplyStream):
                while reply.qsize():
                    await discord_message.channel.send(reply.get().as_str())
                    await asyncio.sleep(0.01)
            else:
                await discord_message.channel.send(reply.as_str())
        except Exception as e:
            await discord_message.channel.send(
                _generate_error_entry(discord_message, e).as_str())

    def run_client(self):
        if not self.token or not self.guild:
            raise ValueError("Cannot connect - missing authentication."
                             "'token' and 'guild' must be provided when "
                             "using the Discord client. Specify these "
                             "values in the dictionary for the client "
                             "as {\"token\": \"foo_token\", \"guild\": "
                             "\"foo_guild\"}")
        _token = self.token
        del self.token

        try:
            self.run(_token)
        except Exception as e:
            raise RuntimeError("DiscordClient ran in to a problem. "
                               "Please ensure that all data is provided "
                               "correctly in settings.py."
                               f"Excact error message: \"{e}\"")
