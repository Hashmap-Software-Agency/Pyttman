import argparse
import sys
from datetime import datetime

from pyttman.tools.pyttmancli.executor import Runner
from pyttman.tools.pyttmancli.terraforming import TerraFormer, bootstrap_environment


def run(argv=None):

    runners = None

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
        bootstrap_environment(devmode=True, module=app_name).run()
    elif command == "runclient":
        print(f" {datetime.now()} --> Bootstrapping environment for app '{app_name}'...", end=" ")
        try:
            if (runner := bootstrap_environment(module=app_name)) is not None:
                print(f" {datetime.now()} --> Starting app using '{runner.client.name}'...", end=" ")
            else:
                raise RuntimeError("Client bootstrapping failed")
        except Exception as e:
            print(f"failed.")
            raise e
        else:
            print(f"success!")
            runner.run()
    else:
        from pyttman import __version__
        print(f"Pyttman CLI, version {__version__}")
        print(f"\nSupported commands:\n\n "
              f"* newapp [<app name>] - "
              "Start a new app project. Creates files and "
              "directories in the current directory\n "
              "* dev [<app name>] - Starts running the app with a "
              "CLI client for development purposes\n "
              "* runclient [<app name>]- Starts your app using the "
              "Client class defined in settins.py. This is "
              "the standard production mode for Pyttman apps.\n")
