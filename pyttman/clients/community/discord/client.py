
# The following license refers to the license to the Discord module,
# published by Rapptz, available on GitHub: https://github.com/rapptz/discord.py
# The Pyttman project implements and subclasses modules from the Discord package
# to make it easier for users to integrate with this powerful platform.
# All credit for the work put in to the Discord module goes to Rapptz, where it's due.

# discord.py MIT license

#           The MIT License (MIT)
#
#           Copyright (c) 2015-present Rapptz
#
#           Permission is hereby granted, free of charge, to any person obtaining a
#           copy of this software and associated documentation files (the "Software"),
#           to deal in the Software without restriction, including without limitation
#           the rights to use, copy, modify, merge, publish, distribute, sublicense,
#           and/or sell copies of the Software, and to permit persons to whom the
#           Software is furnished to do so, subject to the following conditions:
#
#           The above copyright notice and this permission notice shall be included in
#           all copies or substantial portions of the Software.
#
#           THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#           OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#           FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#           AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#           LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#           FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#           DEALINGS IN THE SOFTWARE.

# Pyttman MIT license

#     MIT License
#
#      Copyright (c) 2021-present Simon Olofsson
#
#      Permission is hereby granted, free of charge, to any person obtaining a copy
#      of this software and associated documentation files (the "Software"), to deal
#      in the Software without restriction, including without limitation the rights
#      to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#      copies of the Software, and to permit persons to whom the Software is
#      furnished to do so, subject to the following conditions:
#
#      The above copyright notice and this permission notice shall be included in all
#      copies or substantial portions of the Software.
#
#      THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#      IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#      FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#      AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#      LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#      OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#      SOFTWARE.
import asyncio
import warnings
from datetime import datetime

import discord
from typing import Union
from pyttman.clients.builtin.base import BaseClient
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

        # Vacuum all attributes found in __slots__ in the discord.Message object
        for attr_name in message.__slots__:
            try:
                attrs[attr_name] = getattr(message, attr_name)
            except AttributeError:
                # It was likely a method - skip it
                continue

        # Accessing the protected _state field is unfortunately necessary here
        discord_message = DiscordMessage(state=attrs.get("_state"),
                                         data=attrs, **attrs)

        # Verify that the conditions as set by the user are fulilled with pre- and/or suffixes
        msg_as_str: str = discord_message.as_str()
        if self.message_startswith and not msg_as_str.startswith(self.message_startswith) \
                or self.message_endswith and not msg_as_str.endswith(self.message_endswith):
            return

        # Get the reply from the application logic developed by the user and send it in
        # the channel from the original message
        reply: Union[Reply, ReplyStream] = self.message_router.get_reply(discord_message)
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
            raise RuntimeError("DiscordClient ran in to a problem. Please ensure "
                               f"that all data is provided correctly in settings.py."
                               f"Excact error message: \"{e}\"")
