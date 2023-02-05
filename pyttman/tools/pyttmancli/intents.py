import code
import os
import pathlib
import traceback
import requests

from time import sleep
from pyttman.version import __version__ as pyttman_version
from pyttman.core.mixins import PyttmanCliComplainerMixin
from pyttman.core.decorators import LifeCycleHookType
from pyttman.core.entity_parsing.fields import TextEntityField
from pyttman.core.intent import Intent
from pyttman.tools.pyttmancli import TerraFormer, bootstrap_app
from pyttman.core.containers import (
    Message,
    ReplyStream,
    Reply
)


class ShellMode(Intent, PyttmanCliComplainerMixin):
    """
    Opens an interactive shell in their application,
    useful for debugging.
    """
    lead = ("shell",)
    example = "pyttman shell <app name>"
    help_string = "Opens a Python interactive shell with access to modules, " \
                  "app settings and the Pyttman 'app' object."
    app_name = TextEntityField()

    def respond(self, message: Message) -> Reply | ReplyStream:
        app_name = message.entities["app_name"]
        if complaint := self.complain_app_not_found(app_name):
            return Reply(complaint)
        app = bootstrap_app(devmode=True, module=app_name)
        app.hooks.trigger(LifeCycleHookType.before_start)
        global_variables = globals().copy()
        global_variables.update(locals())
        shell = code.InteractiveConsole(global_variables)
        shell.interact()
        return Reply("Exited shell")


class CreateNewApp(Intent, PyttmanCliComplainerMixin):
    """
    Create a new Pyttman app. The directory is terraformed
    and prepared with a template project.
    """
    app_name = TextEntityField()
    lead = ("new",)
    trail = ("app",)
    ordered = True
    example = "pyttman new app <app name>"
    help_string = "Creates a new Pyttman app project in current directory " \
                  "from a template.\n" \
                  f"Example: {example}"

    def respond(self, message: Message) -> Reply | ReplyStream:
        num_retries = 3
        net_err = None
        app_name = message.entities["app_name"]
        terraformer = TerraFormer(app_name=app_name,
                                  url=self.storage["template_url"])

        print(f"- Creating project '{app_name}'.")
        print(f"- Downloading the latest official project "
              f"template from GitHub", end="\n")

        for i in range(num_retries):
            print(f"- Attempt [{i + 1}/{num_retries}]:", end=" ")
            try:
                terraformer.terraform()
            except requests.exceptions.ConnectionError as e:
                print("failed.",
                      "Cannot connect to the server, "
                      "trying again in 5 seconds...",
                      end="\n",
                      sep=" ")
                sleep(5)
                net_err = e
                continue
            except Exception as e:
                print(f"errors occurred: '{e}'. See full traceback below.",
                      traceback.format_exc(), end="\n\n", sep="\n\n")
                raise e
            else:
                print("success!")
                break

        if net_err is not None:
            raise RuntimeError(f"The project could not be created.")
        return Reply(f"Wondering what to do next? Visit the "
                     f"Pyttman Wiki to follow our Get Started guide at "
                     f"https://github.com/dotchetter/Pyttman/wiki/Tutorial")


class RunAppInDevMode(Intent, PyttmanCliComplainerMixin):
    """
    Run a Pyttman app in dev mode. This sets "DEV_MODE"
    to True and opens a chat interface in the terminal.
    """
    app_name = TextEntityField()
    fail_gracefully = True
    lead = ("dev",)
    example = "pyttman dev <app name>"
    help_string = "Run a Pyttman app in dev mode. Dev mode sets " \
                  "'pyttman.DEBUG' to True, enabling verbose outputs " \
                  "as defined in your app.\nThe app is started using " \
                  "a CliClient for you to start chatting with your app " \
                  "with minimal overhead.\n" \
                  f"Example: {example}"

    def respond(self, message: Message) -> Reply | ReplyStream:
        app_name = message.entities["app_name"]
        if complaint := self.complain_app_not_found(app_name):
            return Reply(complaint)
        try:
            app = bootstrap_app(devmode=True, module=app_name)
            app.hooks.trigger(LifeCycleHookType.before_start)
        except Exception as e:
            if self.fail_gracefully is False:
                raise e
            print(traceback.format_exc())
            return Reply("The app could not start due to issues with "
                         "bootstrapping, see traceback above.")
        self.storage.put("app", app)
        self.storage.put("ready", True)
        return Reply(f"- Starting app '{app_name}' in dev mode...")


class RunAppInClientMode(Intent, PyttmanCliComplainerMixin):
    """
    Run a Pyttman in production mode. Client is configured
    settings.py.
    """
    fail_gracefully = True
    lead = ("runclient",)
    example = "pyttman runclient <app name>"
    help_string = "Run a Pyttman app in client mode. This is the " \
                  "standard production mode for Pyttman apps.\nThe " \
                  "app will be started using the client defined in " \
                  "settings.py under 'CLIENT'.\n" \
                  f"Example: {example}"

    app_name = TextEntityField()

    def respond(self, message: Message) -> Reply | ReplyStream:
        app_name = message.entities["app_name"]
        if complaint := self.complain_app_not_found(app_name):
            return Reply(complaint)
        try:
            app = bootstrap_app(devmode=False, module=app_name)
            app.hooks.trigger(LifeCycleHookType.before_start)
        except Exception as e:
            if self.fail_gracefully is False:
                raise e
            print(traceback.format_exc())
            return Reply("The app could not start due to issues with "
                         "bootstrapping, see traceback above.")
        self.storage.put("app", app)
        self.storage.put("ready", True)
        return Reply(f"- Starting app '{app_name}' in client mode...")


class RunScript(Intent, PyttmanCliComplainerMixin):
    """
    Runs a single Python file within a Pyttman app context
    """
    fail_gracefully = True
    lead = ("runfile",)
    example = "pyttman runfile <app name> <file.py>"
    help_string = "Run a singe file within a Pyttman app context. " \
                  f"Example: {example}"

    script_file_name = TextEntityField()
    app_name = TextEntityField(prefixes=(script_file_name,))

    def respond(self, message: Message) -> Reply | ReplyStream:
        app_name = message.entities["app_name"]
        script_file = message.entities["script_file_name"]

        if complaint := self.complain_app_not_found(app_name):
            return Reply(complaint)
        if script_file is None:
            return Reply("Filename must be entered, as a '.py' file. "
                         f"Example: {self.example}")

        script_file = pathlib.Path(script_file)
        app = bootstrap_app(devmode=True, module=app_name)
        app.hooks.trigger(LifeCycleHookType.before_start)
        global_variables = globals().copy()
        global_variables.update(locals())
        shell = code.InteractiveConsole(global_variables)

        with open(script_file.as_posix(), "r") as f:
            source = f.read()
            code_obj = compile(source, script_file.as_posix(), "exec")
            shell.runcode(code_obj)
        return Reply(f"Script file executed successfully.")


class CreateNewAbilityIntent(Intent, PyttmanCliComplainerMixin):
    """
    Create a new Ability in a Pyttman application. A new directory
    and a 'ability.py' file is created for you in the app directory.
    """
    lead = ("new",)
    trail = ("ability",)
    ordered = True
    example = "pyttman new ability <ability name> app <app name>"
    help_string = "Create a new file with an Ability class as " \
                  "a template for new Ability classes for your app.\n" \
                  f"Example: {example}"

    ability_name = TextEntityField()
    app_name = TextEntityField(prefixes=(ability_name,))

    def respond(self, message: Message) -> Reply | ReplyStream:
        files_to_create = ("__init__.py", "ability.py",
                           "intents.py", "models.py")
        ability_name = message.entities["ability_name"]
        app_name = message.entities["app_name"]
        if complaint := self.complain_app_not_found(app_name):
            return Reply(complaint)
        else:
            app_name = pathlib.Path(app_name)

        abilities_parent_catalog = app_name / "abilities"
        ability_catalog = abilities_parent_catalog / ability_name

        if not abilities_parent_catalog.exists():
            os.mkdir(abilities_parent_catalog)
            init_file_path = abilities_parent_catalog / "__init__.py"
            with open(init_file_path, "w", encoding="utf-8") as f:
                # Empty file is OK
                pass

        if not ability_catalog.exists():
            os.mkdir(ability_catalog)
        else:
            return Reply("There's already an ability with that name.")

        for file in files_to_create:
            rel_path = ability_catalog / file
            with open(rel_path, "w", encoding="utf-8") as f:
                f.write("\n# Created by Pyttman ")
        return Reply(f"Created ability '{ability_name}'.")


class VersionInfo(Intent):
    """
    Returns the version info about this Pyttman installation.
    """
    lead = ("-v", "v",)
    example = "pyttman -V"
    help_string = "Returns the Pyttman build version. " \
                  f"Example: {example}"

    def respond(self, message: Message) -> Reply | ReplyStream:
        return Reply(pyttman_version)
