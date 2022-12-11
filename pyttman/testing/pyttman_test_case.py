from pathlib import Path
from unittest import TestCase

from pyttman.core.exceptions import PyttmanProjectInvalidException
from pyttman.tools.pyttmancli import bootstrap_app


class PyttmanTestCase(TestCase):

    devmode = False
    application_abspath = None
    app_name = None

    def __init__(self, *args, **kwargs):
        relative_root_directory = Path.cwd().parent.parent
        if self.app_name is None:
            self.app_name = relative_root_directory.name

        try:
            self.app = bootstrap_app(
                devmode=self.devmode,
                module=self.app_name,
                application_abspath=self.application_abspath or relative_root_directory)
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
