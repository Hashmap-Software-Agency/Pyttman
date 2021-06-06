import os
import shutil
from datetime import datetime
from pathlib import Path

from py7zr import unpack_7zarchive


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
        print("\n To start your new app, develop Features and "
              "then use pyttman-cli to start it. Test it with "
              "the 'pyttman-cli dev' command to get a CLI shell "
              "for chatting with your app while developing.")

    def get_info(self):
        return f"Extraction dir: {self.extraction_dir}, " \
               f"Source: {self.source}"