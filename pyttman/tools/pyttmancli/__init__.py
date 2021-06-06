import sys
import argparse

from pyttman.tools.pyttmancli.executor import Runner
from pyttman.tools.pyttmancli.terraforming import TerraFormer


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

    if command == "newapp":
        app_name = options.args.pop()
        terraformer = TerraFormer(app_name=app_name)
        terraformer.terraform()
    elif command == "dev":
        app_name = options.args.pop()
        runner = Runner(app_name)
        runner.run()
    else:
        from pyttman import __version__
        print(f"\nPyttman CLI, version {__version__}")
        print(f"\nSupported commands:\n * newapp [<app name>] - "
              "Start a new app project. Creates files and "
              "directories in the current directory\n * dev "
              "[<app name>] - Starts running the app with a "
              "CLI client for development purposes\n\n")
