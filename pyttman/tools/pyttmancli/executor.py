from importlib import import_module
from pathlib import Path

from pyttman.clients.cli import CliClient


class Runner:
    """
    Runs a pyttman app based on the settings in
    the app settings.py file.
    """
    def __init__(self, app_name: str):
        self.app_catalog = Path.cwd() / Path(app_name)
        self.client = None
        try:
            self.app_settings = import_module(f"{self.app_catalog}.settings")
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Pyttman cannot find the settings file for an app called "
                                      f"'{app_name}' in the current directory. Remember to run "
                                      f"pyttman-cli run <appname> in the parent folder of your "
                                      f"app.")

    def run(self):
        import pyttman
        pyttman.load_settings(self.app_settings)

        from pyttman.core.parsing.routing import LinearSearchFirstMatchingRouter
        router = LinearSearchFirstMatchingRouter()
        router.features = self.app_settings.FEATURES

        self.client = CliClient(router)  # Todo - parse from settings
        self.client.run()
