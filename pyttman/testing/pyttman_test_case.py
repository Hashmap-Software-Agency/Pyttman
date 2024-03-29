import traceback
from pathlib import Path
from unittest import TestCase

from pyttman.core.decorators import LifeCycleHookType
from pyttman.core.exceptions import PyttmanProjectInvalidException
from pyttman.tools.pyttmancli import bootstrap_app


class PyttmanTestCase(TestCase):
    devmode = False
    application_abspath = None
    app_name = None
    override_devmode_warning = False

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
            print(traceback.format_exc())
            raise PyttmanProjectInvalidException(
                "\n\nPyttman could not boostrap the application for "
                "testing. Full traceback above"
            ) from e

        super().__init__(*args, **kwargs)
        if not any((self.devmode, self.app.settings.DEV_MODE, self.override_devmode_warning)):
            raise Warning("Warning! This test class does not declare 'devmode' as a "
                          "True, and 'DEV_MODE' in settings.py for "
                          "this app is False. This could potentially lead to "
                          "a test executing to production environment. "
                          "To override this warning, set 'override_devmode_warning = True' "
                          "as a class variable in this unit test.")
        self.app.settings.DEV_MODE = self.devmode
        self.app.hooks.trigger(LifeCycleHookType.before_start)

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
