
"""
This file contains Intents and Ability classes which make out
the Pyttman cli tool, used to administer, bootstrap and create
Pyttman app for users of the framework.

Are you a Pyttman developer or a contributor and want to extend
the 'pyttman' terminal tool with new functionality?

Add Intents to the PyttmanCLI Ability and ensure that you
overload the 'description' and 'example' fields of the Intent
classes, since they provide essential data for users when
using the tool in the terminal.

"""
import argparse
import sys
import typing

from pyttman.core.communication.models.containers import Message
from pyttman.core.middleware.routing import FirstMatchingRouter
from pyttman.tools.pyttmancli.executor import Runner
from pyttman.tools.pyttmancli.terraforming import TerraFormer, \
    bootstrap_environment
from pyttman.tools.pyttmancli.terraforming import bootstrap_environment, \
    TerraFormer
from pyttman.tools.pyttmancli.ability import PyttmanCli


def run(argv=None, dev_args: typing.List = None):
    """
    This function utilizes the Pyttman framework itself,
    to administrate, bootstrap and create Pyttman apps.

    The method is designed to be implicitly called through
    the terminal shell, as argparse is used to extract
    values for parsing.

    For testing purposes if you're a Pyttman developer;
    provide your arguments as a single list of strings
    in the 'dev_args' kwarg instead of using 'argv'.

    This allows the Pyttman cli to work without actual
    terminal arguments.

    :param argv: Args from a terminal shell.
    :param dev_args: Optional developer args in a list of
                     strings, for unit testing the Pyttman CLI
                     or otherwise using it outside of a terminal
                     shell. Defining this argument will automatically
                     disregard the 'argv' arguments
    :return: None
    """
    terminal_message = Message()
    pyttman_cli = PyttmanCli()
    dot = "\u2022"
    default_response = [pyttman_cli.description]
    default_response.extend([f"\n{dot} {i.example}"
                             for i in pyttman_cli.intents])
    default_response = str(" ").join(default_response) + "\n"

    router = FirstMatchingRouter(abilities=[pyttman_cli], help_keyword="help",
                                 intent_unknown_responses=[default_response])

    # Extract args from terminal shell
    if argv is None:
        argv = sys.argv[:]
        arg_parser = argparse.ArgumentParser(prog="Pyttman CLI",
                                             usage="%(prog)s command",
                                             add_help=False,
                                             allow_abbrev=False)
        arg_parser.add_argument("args", nargs="*")

        try:
            command = argv[1]
        except IndexError:
            command = ""

        options, args = arg_parser.parse_known_args(argv[2:])
        terminal_message = Message(command.split() + options.args)

    elif dev_args is not None:
        terminal_message = Message(dev_args)

    # Let the Pyttman cli parse the command. If a Runner is created,
    # it's started.
    reply = router.get_reply(terminal_message)
    print(reply.as_str())

    if pyttman_cli.storage.get("ready"):
        pyttman_cli.run_application()
