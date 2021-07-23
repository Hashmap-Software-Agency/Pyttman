from importlib import import_module
from pathlib import Path
import sys

from pyttman.clients.builtin.base import BaseClient


class Runner:
    """
    Runs a pyttman app based on the settings in
    the app settings.py file.
    """

    def __init__(self, app_name: str, client: BaseClient):

        sys.path.insert(0, '')
        self.client = client
        self.app_catalog = Path.cwd() / Path(app_name)

        try:
            self.app_settings = import_module(f"{app_name}.settings")
        except ModuleNotFoundError:
            raise ModuleNotFoundError("Pyttman cannot find the settings "
                                      f"file for an app called '{app_name}' "
                                      f"in the current directory. Remember to "
                                      f"run pyttman-cli run <appname>"
                                      f" in the parent folder of your app.")

    def run(self):
        """
        Runs the client provided at instantiation,
        with the message router also provided.

        Sets pyttman to configured = True, for an
        internal indication that the app was started
        using pyttman-cli.
        :return: None
        """
        self.client.run_client()
