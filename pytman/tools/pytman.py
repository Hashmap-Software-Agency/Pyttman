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
    a Pytman project.
    """

    def __init__(self, app_name: str, source = None):

        self.app_name = app_name
        self.extraction_dir = Path.cwd() / Path(app_name)

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        if source is None:
            self.source = Path(application_path).parent / Path("Lib") / \
                          Path("site-packages") / Path("pytman") / Path("core") / \
                          Path("project_template.7z")
            if not os.path.isfile(self.source):
                raise FileNotFoundError("Pytman cli could not locate the template "
                                        ".7z archive for terraforming. It was expected "
                                        f"to be here: '{self.source}'. If you want, you "
                                        f"can create this structure and place the template "
                                        f"file here, or reinstall Pytman. If you think this "
                                        f"error is our fault - please submit an issue on "
                                        f"GitHub!")
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


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-newapp",
                           dest="folder_name",
                           nargs=1,
                           type=str,
                           help="Starts a new project in the "
                                "current directory")

    parsed_args = argparser.parse_args()

    if parsed_args.folder_name:
        folder_name = parsed_args.folder_name.pop()
        terraformer = TerraFormer(app_name=folder_name)
        terraformer.terraform()
    else:
        from pytman import __version__
        print(f"\n\nPytman CLI, version {__version__}"
              f"\n\nSupported commands:\n\n * -newapp [<app name>] --- "
              "Start a new app project. Creates files and "
              "directories in the current directory", end="\n\n")
