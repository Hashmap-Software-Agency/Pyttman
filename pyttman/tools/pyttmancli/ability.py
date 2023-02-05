import pyttman
import pyttman.tools.pyttmancli.intents as intents
from pyttman.core.internals import PyttmanApp
from pyttman.core.ability import Ability


class PyttmanCli(Ability):
    """
    Encapsulates the Pyttman CLI tool 'pyttman'
    used in the terminal by framework users.
    """
    intents = (
        intents.CreateNewApp,
        intents.RunAppInDevMode,
        intents.RunAppInClientMode,
        intents.CreateNewAbilityIntent,
        intents.ShellMode,
        intents.VersionInfo,
        intents.RunScript,
    )

    description = f"\nPyttman v{pyttman.__version__}\n\n" \
                  "For help about a commend, type pyttman help [command]" \
                  f"\n\nSupported commands:\n"

    def before_create(self):
        self.storage.put("app", None)
        self.storage.put("ready", False)
        self.storage.put("template_url",
                         "https://github.com/dotchetter/pyttman-"
                         "project-template/archive/refs/heads/main.zip")

    def run_application(self) -> None:
        """
        Runs a Pyttman application with its Runner context
        as provided.
        :return: None
        """
        # noinspection PyTypeChecker, PyUnusedLocal
        # #(used for attribute access in completion)
        app: PyttmanApp = None
        if (app := self.storage.get("app")) is not None:
            print(f"- Ability classes loaded: "
                  f"{app.client.message_router.abilities}")
            app.start()
        else:
            raise RuntimeError("No Runner provided, app cannot start. "
                               "Exiting...")
