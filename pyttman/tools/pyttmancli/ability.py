import pyttman

from pyttman.core.ability import Ability
from pyttman.tools.pyttmancli import Runner
from pyttman.tools.pyttmancli.intents import CreateNewApp, RunAppInDevMode, \
    RunAppInClientMode


class PyttmanCli(Ability):
    """
    Encapsulates the Pyttman CLI tool 'pyttman'
    used in the terminal by framework users.
    """
    intents = (CreateNewApp,
               RunAppInDevMode,
               RunAppInClientMode)

    description = f"\nPyttman v{pyttman.__version__}\n\n" \
                  "For help about a commend, type pyttman help [command]" \
                  f"\n\nSupported commands:\n"

    def configure(self):
        responses = {"NO_APP_NAME_MSG": "Please provide a name "
                                        "for your app."}
        self.storage.put("runner", None)
        self.storage.put("ready", False)
        self.storage.put("template_url",
                         "https://github.com/dotchetter/pyttman-"
                         "project-template/archive/refs/heads/main.zip")
        self.storage |= responses

    def run_application(self) -> None:
        """
        Runs a Pyttman application with its Runner context
        as provided.
        :return: None
        """
        # noinspection PyTypeChecker, PyUnusedLocal
        # #(used for attribute access in completion)
        runner: Runner = None
        if (runner := self.storage.get("runner")) is not None:
            print(f"- Ability classes loaded: "
                  f"{runner.client.message_router.abilities}")
            runner.run()
        else:
            raise RuntimeError("No Runner provided, app cannot start. "
                               "Exiting...")
