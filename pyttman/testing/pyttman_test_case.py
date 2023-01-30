from copy import copy
from pathlib import Path
from unittest import TestCase

from pyttman.core.exceptions import PyttmanProjectInvalidException
from pyttman.tools.pyttmancli import bootstrap_app


class PyttmanTestCase(TestCase):
    devmode = False
    application_abspath = None
    app_name = None

    def __init__(self, *args, **kwargs):
        if self.application_abspath is None:
            self.application_abspath = self.find_app_path()
        if self.app_name is None:
            self.app_name = self.application_abspath.name

        try:
            self.app = bootstrap_app(
                devmode=self.devmode,
                module=self.app_name,
                application_abspath=self.application_abspath.parent)
        except Exception as e:
            raise PyttmanProjectInvalidException(
                "\n\nPyttman could not boostrap the application for "
                "testing since it wasn't found automatically.\n"
                "Pyttman presumes the tests to be located in: "
                "'project_root/tests/'.\nIf this is no longer the case, "
                "you can explicitly provide the path to "
                "your project root as: 'application_abspath = "
                "'/users/home/.../name_of_pyttman_app' as a class variable in "
                "the test suite.") from e
        super().__init__(*args, **kwargs)

    @staticmethod
    def find_app_path(start_dir: Path = None) -> Path:
        """
        Look for signature catalog which looks like a
        Pyttman app root directory.

        Walk up the file structure until the directory is found.
        :raise ModuleNotFoundError: The file hierarchy was exhausted
        and no pyttman app directory wasn't found
        """
        sought_file = "settings.py"
        start_dir = start_dir or Path.cwd()
        next_dir = start_dir
        while not next_dir.joinpath(sought_file).exists():
            if next_dir.parent == start_dir:
                raise ModuleNotFoundError(
                    "Could not find a Pyttman app in the "
                    "same directory as the test, or in any "
                    "parent folder above it. Is the test "
                    "module placed in a Pyttman application?")
            next_dir = next_dir.parent
        return next_dir
