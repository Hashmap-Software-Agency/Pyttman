import argparse
import concurrent
import sys
from datetime import datetime

from pyttman.tools.pyttmancli.executor import Runner
from pyttman.tools.pyttmancli.terraforming import TerraFormer, bootstrap_environment


def run(argv=None):
    if argv is None:
        argv = sys.argv[:]

    argparser = argparse.ArgumentParser(prog="Pyttman CLI",
                                        usage="%(prog)s command",
                                        add_help=False,
                                        allow_abbrev=False)
    argparser.add_argument("args", nargs="*")

    try:
        command = argv[1]
    except IndexError:
        command = None

    options, args = argparser.parse_known_args(argv[2:])

    if command or args:
        try:
            app_name = options.args.pop()
        except IndexError:
            app_name = input("Enter app name (name of the app directory): ")

    if command == "newapp":
        terraformer = TerraFormer(app_name=app_name)
        terraformer.terraform()
    elif command == "dev":
        runners = bootstrap_environment(devmode=True, module=app_name)
        runners.pop().run()
    elif command == "runclients":
        runners = bootstrap_environment(module=app_name)
        # Put the client runtime in a separate processes for concurrent clients
        with concurrent.futures.ThreadPoolExecutor(
                thread_name_prefix="pyttman-client-thread-") as exc:
            for runner in runners:
                print(f" {datetime.now()} --> Starting client '"
                      f"{runner.client.__class__.__name__}'...")
                exc.submit(runner.run)
    else:
        from pyttman import __version__
        print(f"Pyttman CLI, version {__version__}")
        print(f"\nSupported commands:\n\n * newapp [<app name>] - "
              "Start a new app project. Creates files and "
              "directories in the current directory\n * dev "
              "[<app name>] - Starts running the app with a "
              "CLI client for development purposes\n "
              "* runclients - Starts your app with all clients "
              "defined in the CLIENTS list, in parallel. This is "
              "the standard production mode for Pyttman apps.\n")
