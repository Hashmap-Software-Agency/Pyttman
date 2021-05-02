import sys
import os
import argparse
import shutil
from datetime import datetime

from py7zr import unpack_7zarchive

from pathlib import Path


class TerraFormer:
    """
    Terraform a directory to start developing
    a Pyttman project.
    """

    def __init__(self, app_name: str, source=None):

        self.app_name = app_name
        self.extraction_dir = Path.cwd() / Path(app_name)

        application_path = Path(os.path.dirname(os.path.abspath(__file__)))

        if source is None:
            self.source = Path(application_path).parent.parent / Path("core") / \
                          Path("terraform_template") / Path("project_template.7z")
            if not os.path.isfile(self.source):
                raise FileNotFoundError("Pyttman could not locate the template "
                                        ".7z archive for terraforming. It was "
                                        f"expected to be here: '{self.source}'. "
                                        "If you want, you can create this "
                                        "structure and place the template "
                                        f"file here, or reinstall Pyttman. "
                                        f"If you think this error is our fault - "
                                        f"please submit an issue on GitHub!")
        else:
            self.source = source

    def terraform(self):
        print(f"{datetime.now()} - Creating project '{self.app_name}'...")
        shutil.register_unpack_format('7zip', ['.7z'], unpack_7zarchive)
        shutil.unpack_archive(self.source, self.extraction_dir)
        settings_file_path = Path(self.extraction_dir) / Path("settings.py")

        with open(settings_file_path, "a", encoding="utf-8") as settings_file:
            settings_file.write(f"\nAPP_NAME = \"{self.app_name}\"\n")
        print(f"{datetime.now()} - done.")

    def get_info(self):
        return f"Extraction dir: {self.extraction_dir}, " \
               f"Source: {self.source}"


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
    else:
        from pyttman import __version__
        print(f"\nPyttman CLI, version {__version__}")
        print(f"\nSupported commands:\n * newapp [<app name>] - "
              "Start a new app project. Creates files and "
              "directories in the current directory")
