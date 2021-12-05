import warnings
from importlib import import_module
from pathlib import Path
import sys

from pyttman.clients.base import BaseClient


class Runner:
    """
    Runs a pyttman app based on the settings in
    the app settings.py file.
    """

    def __init__(self, app_name: str, client: BaseClient):

        sys.path.insert(0, "")
        self.client = client
        self.app_catalog = Path.cwd() / Path(app_name)

    def run(self):
        """
        Runs the client provided at instantiation,
        with the message router also provided.

        Sets pyttman to configured = True, for an
        internal indication that the app was started
        using pyttman-cli.
        :return: None
        """
        try:
            self.client.run_client()
        except Exception as e:
            warnings.warn(str(e))
