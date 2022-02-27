import sys
import logging
import os
import shutil
import traceback
from datetime import datetime
from importlib import import_module
from pathlib import Path

from py7zr import unpack_7zarchive

import pyttman
from pyttman.clients.builtin.cli import CliClient
from pyttman.core.ability import Ability
from pyttman.core.exceptions import PyttmanProjectInvalidException
from pyttman.core.internals import Settings
from pyttman.core.middleware.routing import AbstractMessageRouter
from pyttman.tools.pyttmancli import Runner


class TerraFormer:
    """
    Terraform a directory to start developing
    a Pyttman project.
    """

    def __init__(self, app_name: str, source=None):

        self.app_name = app_name
        self.extraction_dir = Path.cwd() / Path(app_name)

        application_path = Path(os.path.dirname(os.path.abspath(__file__)))

        if source is None:
            self.source = Path(application_path).parent.parent / \
                          Path("core") / Path("terraform_template") / \
                          Path("project_template.7z")
            if not os.path.isfile(self.source):
                raise FileNotFoundError("Pyttman could not locate the "
                                        "template .7z archive for "
                                        "terraforming. It was expected to be "
                                        f"here: '{self.source}' To "
                                        "solve this problem, reinstall "
                                        "Pyttman. If you think this error "
                                        "is our fault - please submit an "
                                        "issue on GitHub!")
        else:
            self.source = source

    def terraform(self):

        shutil.register_unpack_format('7zip', ['.7z'], unpack_7zarchive)
        shutil.unpack_archive(self.source, self.extraction_dir)
        settings_file_path = Path(self.extraction_dir) / Path("settings.py")

        with open(settings_file_path, "a", encoding="utf-8") as settings_file:
            settings_file.write(f"\nAPP_NAME = \"{self.app_name}\"\n")

    def get_info(self):
        return f"Extraction dir: {self.extraction_dir}, " \
               f"Source: {self.source}"


def bootstrap_environment(module: str = None, devmode: bool = False) -> Runner:
    """
    Bootstraps the framework with modules and configurations
    read from the settings.py found in the current path.

    Configuration for the logger, the clients used and
    Features are parsed, asserted and wrapped in Runner objects
    for the actual app starter to simply call 'run' on.

    :param module: Module in which the app source is located
    :param devmode: Provides only one runner with the CliClient in.
    :return: Runner instance with a ready-to-run Client instance.
    """

    # This enables relative imports
    sys.path.insert(0, Path.cwd().as_posix())

    # First, find the settings.py. It should reside in the current directory
    # provided that the user is currently positioned in the app catalog for
    # their Pyttman project.
    if (Path(module) / "settings.py").exists() is False:
        raise PyttmanProjectInvalidException("No 'settings.py' module "
                                             "found.\nMake sure you are "
                                             "executing the command from "
                                             "within your Pyttman app "
                                             "directory (where the "
                                             "settings.py file is located).")

    try:
        settings_module = import_module(f"{module}.settings")
        settings_names = [i for i in dir(settings_module)
                          if not i.startswith("__")]
        settings_config = {name: getattr(settings_module, name)
                           for name in settings_names}
        settings = Settings(**settings_config)
    except ImportError as e:
        print(traceback.format_exc())
        raise ImportError("An import error occurred when bootstrapping your "
                          "application. Check the modules imported in "
                          "'settings.py' and make sure they're installed and "
                          "spelled correctly.") from e

    if settings is not None:
        pyttman.settings = settings
        pyttman.is_configured = True
    else:
        raise NotImplementedError("Pyttman is improperly configured - "
                                  "settings module for app not found. ")

    # Configure the logger instance for pyttman.logger
    app_name = pyttman.settings.APP_NAME
    if pyttman.settings.APPEND_LOG_FILES:
        file_name = Path(f"{app_name}.log")
    else:
        file_name = Path(
            f"{app_name}-{datetime.now().strftime('%y%m%d-%H-%M-%S')}.log")

    log_file_name = Path(pyttman.settings.LOG_FILE_DIR) / file_name
    logging_handle = logging.FileHandler(
        filename=log_file_name, encoding="utf-8",
        mode="a+" if pyttman.settings.APPEND_LOG_FILES else "w")

    # Assign logging format - added in 1.1.9. Accounts for lower versions
    try:
        logging_format = pyttman.settings.LOG_FORMAT
    except AttributeError:
        logging_format = logging.BASIC_FORMAT

    logging_handle.setFormatter(logging.Formatter(logging_format))
    logger = logging.getLogger("Pyttman logger")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging_handle)

    # Set the configured instance of logger to the pyttman.PyttmanLogger object
    pyttman.logger.LOG_INSTANCE = logger

    # Import the router defined in MESSAGE_ROUTER in settings.py
    message_router_config = settings.MESSAGE_ROUTER\
        .get("ROUTER_CLASS").split(".")
    message_router_class_name = message_router_config.pop()
    message_router_module = ".".join(message_router_config)
    message_router_module = import_module(message_router_module)

    if not (message_router_class := getattr(message_router_module,
                                            message_router_class_name)):
        raise ImportError(f"Pyttman could not find the router "
                          f"'{message_router_class_name} in "
                          f"{message_router_class_name}. "
                          f"Verify the MESSAGE_ROUTER setting in settings.py.")

    # Retrieve the help keyword from settings
    if not (help_keyword := settings.MESSAGE_ROUTER.get("HELP_KEYWORD")):
        raise AttributeError("'HELP_KEYWORD' not defined in settings.py. "
                             "Please define a word for the automatic "
                             "help page generation to trigger on in your "
                             "app whenever it is present as the first "
                             "occurring string in a message.\nExample: "
                             "'HELP_KEYWORD' = 'help'")

    # Retrieve command-unknown-responses from settings
    if not (command_unknown_responses := settings.MESSAGE_ROUTER.
            get("COMMAND_UNKNOWN_RESPONSES")):
        raise ValueError("There are no responses provided for when "
                         "no intents match a query. Define these in "
                         "MESSAGE_ROUTER['COMMAND_UNKNOWN_RESPONSES'] as "
                         "a list of strings")

    # Import the client classes defined in CLIENTS in settings.py
    if not len(settings.CLIENT) and not devmode:
        raise ValueError("A Client is required for Pyttman to "
                         "start your app in Client mode. Define a Client "
                         "in settings.py. Refer to the documentation for "
                         "examples.")

    # Set the abilities of the router to the abilities from settings.py
    ability_objects_set = set()
    for ability in settings.ABILITIES:
        assert not isinstance(ability, Ability), \
            f"The ability '{ability}' is instantiated. Please redefine " \
            f"this ability as only the reference to the class, " \
            f"as shown in the docs. "

        ability_module_config = ability.split(".")
        ability_class_name = ability_module_config.pop()
        ability_module_name = ".".join(ability_module_config)
        ability_module = import_module(ability_module_name)
        ability_class = getattr(ability_module, ability_class_name)

        # Instantiate the ability class and traverse over its intents.
        # Validate.
        intent_instance = ability_class()
        assert issubclass(ability_class, Ability), \
            f"'{intent_instance.__class__.__name__}' " \
            f"is not a subclass of 'Ability'. " \
            f"Check your ABILITIES list in settings.py and verify that " \
            f"all classes defined are Ability subclasses."
        ability_objects_set.add(intent_instance)

    assert len(ability_objects_set), "No Ability classes were provided the " \
                                     "ABILITIES list in settings.py"

    # Instantiate router and provide the APP_NAME from settings
    message_router: AbstractMessageRouter = message_router_class(
        abilities=list(ability_objects_set),
        intent_unknown_responses=command_unknown_responses,
        help_keyword=help_keyword)

    # If devmode is active, return only one CliClient in a runner.
    if devmode:
        pyttman.settings.DEV_MODE = True
        client = CliClient(message_router=message_router)
        return Runner(settings.APP_NAME, client)

    # Start the client
    if not isinstance(settings.CLIENT, dict):
        raise TypeError("The CLIENT config must be a single dict, "
                        "containing the full reference to the client "
                        "class")
    try:
        client_class_config = settings.CLIENT.pop("class").split(".")
    except Exception:
        raise ValueError("The dictionary containing Client configuration "
                         "must contain the key 'class', which should be "
                         "the import path for the Client class. Verify "
                         "the 'CLIENT' property in settings.py. See the "
                         "Client documentation for more help on this subject.")
    try:
        client_class_name = client_class_config.pop()
        module_name = ".".join(client_class_config)
        module = import_module(module_name)

        # Provide the client with message_router and runner with client
        client_class = getattr(module, client_class_name)
    except Exception as e:
        raise RuntimeError(f"Cannot start client. Check "
                           f"the following error and correct "
                           f"any syntax error in settings.py: "
                           f"\n{e}") from e
    client = client_class(message_router=message_router, **settings.CLIENT)

    # Create a log entry for app start
    pyttman.logger.log(f" -- App {app_name} started: {datetime.now()} -- ")
    return Runner(settings.APP_NAME, client)
