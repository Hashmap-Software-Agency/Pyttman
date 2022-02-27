import pathlib
import typing

from pyttman.core.communication.models.containers import Message, \
    ReplyStream, \
    Reply
from pyttman.core.entity_parsing.fields import TextEntityField
from pyttman.core.intent import Intent
from pyttman.tools.pyttmancli import TerraFormer, bootstrap_environment


class CreateNewApp(Intent):
    """
    Intent class for creating a new Pyttman app.
    The directory is terraformed and prepared
    with a template project.
    """
    lead = ("new",)
    trail = ("app",)
    ordered = True
    example = "pyttman new app <app name>"
    help_string = "Creates a new Pyttman app project in current directory " \
                  "from a template.\n" \
                  f"Example: {example}"

    class EntityParser:
        app_name = TextEntityField()

    def respond(self, message: Message) -> Reply | ReplyStream:
        if (app_name := message.entities.get("app_name")) is None:
            return Reply(self.storage.get("NO_APP_NAME_MSG"))

        app_name = app_name
        print(f"- Creating project '{app_name}'...", end=" ")
        try:
            terraformer = TerraFormer(app_name=app_name)
            terraformer.terraform()
        except Exception as e:
            print("errors occurred.")
            return Reply(f"{e.__class__.__name__}: {e}")
        print("done.")
        return Reply(f"- Check out your new app '{app_name}' in "
                     f"the current directory. Feel free to visit the "
                     f"Pyttman Wiki to follow our Get Started guide at "
                     f"https://github.com/dotchetter/Pyttman/wiki/Tutorial")


class RunAppInDevMode(Intent):
    """
    Intent class for running a Pyttman app in dev mode,
    meaning the "DEV_MODE" flag is set to True in the app
    to provide verbose outputs which are user defined
    and the CliClient is used as the primary front end.
    """
    lead = ("dev",)
    example = "pyttman dev <app name>"
    help_string = "Run a Pyttman app in dev mode. Dev mode sets " \
                  "'pyttman.DEBUG' to True, enabling verbose outputs " \
                  "as defined in your app.\nThe app is started using " \
                  "a CliClient for you to start chatting with your app " \
                  "with minimal overhead.\n" \
                  f"Example: {example}"

    class EntityParser:
        app_name = TextEntityField()

    def respond(self, message: Message) -> Reply | ReplyStream:
        if (app_name := message.entities.get("app_name")) is None:
            return Reply(self.storage.get("NO_APP_NAME_MSG"))

        app_name = app_name.value
        if not pathlib.Path(app_name).exists():
            return Reply(f"- App '{app_name}' was not found here, "
                         f"verify that a Pyttman app directory named "
                         f"'{app_name}' exists.")
        try:
            runner = bootstrap_environment(devmode=True, module=app_name)
        except Exception as e:
            print("errors occurred:")
            return Reply(f"\t{e.__class__.__name__}: {e}")
        self.storage.put("runner", runner)
        self.storage.put("ready", True)
        return Reply(f"- Starting app '{app_name}' in dev mode...")


class RunAppInClientMode(Intent):
    """
    Intent class for running Pyttman Apps
    in Client mode.
    """
    lead = ("runclient",)
    example = "pyttman runclient <app name>"
    help_string = "Run a Pyttman app in client mode. This is the " \
                  "standard production mode for Pyttman apps.\nThe " \
                  "app will be started using the client defined in " \
                  "settings.py under 'CLIENT'.\n" \
                  f"Example: {example}"

    class EntityParser:
        app_name = TextEntityField()

    def respond(self, message: Message) -> Reply | ReplyStream:
        if (app_name := message.entities.get("app_name")) is None:
            return Reply(self.storage.get("NO_APP_NAME_MSG"))

        app_name = app_name
        if not pathlib.Path(app_name).exists():
            return Reply(f"- App '{app_name}' was not found here, "
                         f"verify that a Pyttman app directory named "
                         f"'{app_name}' exists.")
        try:
            runner = bootstrap_environment(devmode=False, module=app_name)
        except Exception as e:
            print("errors occurred:")
            return Reply(f"\t{e.__class__.__name__}: {e}")
        self.storage.put("runner", runner)
        self.storage.put("ready", True)
        return Reply(f"- Starting app '{app_name}' in client mode...")


class CreateNewAbilityIntent(Intent):
    lead = ("new",)
    trail = ("ability",)
    ordered = True
    example = "pyttman new ability <ability name> app <app name>"
    help_string = "Create a new file with an Ability class as " \
                  "a template for new Ability classes for your app.\n" \
                  f"Example: {example}"

    class EntityParser:
        ability_name = TextEntityField()
        app_name = TextEntityField(prefixes=("app",))

    def respond(self, message: Message) -> Reply | ReplyStream:
        raise NotImplementedError
