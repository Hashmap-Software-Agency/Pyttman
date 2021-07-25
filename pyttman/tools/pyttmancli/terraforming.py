import logging
import os
import shutil
import traceback
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import List

from py7zr import unpack_7zarchive

import pyttman
from pyttman import Feature
from pyttman.clients.builtin.cli import CliClient
from pyttman.core.parsing.routing import AbstractMessageRouter
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
            self.source = Path(application_path).parent.parent / Path("core") / \
                          Path("terraform_template") / Path("project_template.7z")
            if not os.path.isfile(self.source):
                raise FileNotFoundError("Pyttman could not locate the template "
                                        ".7z archive for terraforming. It was "
                                        f"expected to be here: '{self.source}'. "
                                        "If you want, you can create this "
                                        "structure and place the template "
                                        f"file here, or reinstall Pyttman. "
                                        f"If you think this error is our fault - "
                                        f"please submit an issue on GitHub!")
        else:
            self.source = source

    def terraform(self):
        print(f"\n\t{datetime.now()} - Creating project '{self.app_name}'...")
        shutil.register_unpack_format('7zip', ['.7z'], unpack_7zarchive)
        shutil.unpack_archive(self.source, self.extraction_dir)
        settings_file_path = Path(self.extraction_dir) / Path("settings.py")

        with open(settings_file_path, "a", encoding="utf-8") as settings_file:
            settings_file.write(f"\nAPP_NAME = \"{self.app_name}\"\n")
        print(f"\t{datetime.now()} - done.")
        print("\nTip! To start your new app, develop Features and "
              "then use pyttman-cli to start it. Test it with "
              "the 'pyttman-cli dev' command to get a CLI shell "
              "for chatting with your app while developing.")

    def get_info(self):
        return f"Extraction dir: {self.extraction_dir}, " \
               f"Source: {self.source}"


def bootstrap_environment(project_path: str = None,
                          devmode: bool = False) -> List:
    """
    Bootstraps the framework with modules and configurations
    read from the settings.py found in the current path.

    Configuration for the logger, the clients used and
    Features are parsed, asserted and wrapped in Runner objects
    for the actual app starter to simply call 'run' on.

    :param project_path: path to the project at app root level.
                         (same as settings.py). This parameter is
                         NOT needed if invoked where the settings
                         module for the app is located.
    :param devmode: Provides only one runner with the CliClient in.
    :return: List of Runner objects, with ready-to-start clients
    """
    if project_path is None:
        project_path = ""
    runners = []

    # First, find the settings.py. It should reside in the current directory
    # provided that the user is currently positioned in the app catalog for
    # their Pyttman project.
    try:
        settings = import_module(f"{project_path}.settings")
    except ImportError:
        raise ImportError("No 'settings.py' module found. Make sure you are "
                          "executing the command from within your Pyttman app "
                          "directory (where the settings.py file is located).")

    if settings is not None:
        pyttman.settings = settings
        pyttman.is_configured = True
    else:
        raise NotImplementedError("Pyttman is improperly configured - settings "
                                  "module for app not found. ")

    # Configure the logger instance for pyttman.logger
    app_name = pyttman.settings.APP_NAME
    if pyttman.settings.APPEND_LOG_FILES:
        file_name = Path(f"{app_name}.log")
    else:
        file_name = Path(f"{app_name}-{datetime.now().strftime('%y%m%d-%H-%M-%S')}.log")

    log_file_name = Path(pyttman.settings.LOG_FILE_DIR) / file_name
    logging_handle = logging.FileHandler(filename=log_file_name, encoding="utf-8",
                                         mode="a+" if pyttman.settings.APPEND_LOG_FILES else "w")
    logging_handle.setFormatter(logging.Formatter("%(asctime)s:%(levelname)"
                                                  "s:%(name)s: %(message)s"))
    _logger = logging.getLogger("Pyttman logger")
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(logging_handle)

    # Set the configured instance of logger to the pyttman.PyttmanLogger object
    pyttman.logger.LOG_INSTANCE = _logger

    # Import the router defined in MESSAGE_ROUTER in settings.py
    message_router_config = settings.MESSAGE_ROUTER.get("ROUTER_CLASS").split(".")
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
                             "app whenever it is present as the first occurring "
                             "string in a message.\nExample: 'HELP_KEYWORD' = 'help'")

    # Retrieve command-unknown-responses from settings
    if not (command_unknown_responses := settings.MESSAGE_ROUTER.
            get("COMMAND_UNKNOWN_RESPONSES")):
        raise ValueError("There are no responses provided for when "
                         "no commands match a query. Define these in "
                         "MESSAGE_ROUTER['COMMAND_UNKNOWN_RESPONSES'] as "
                         "a list of strings")

    # Import the client classes defined in CLIENTS in settings.py
    if not len(settings.CLIENTS):
        raise ValueError("At least one Client is required for Pyttman to "
                         "start your app in Client mode. Define a Client "
                         "in settings.py. Refer to the documentation for "
                         "examples.")

    # Set the features of the router to the features from settings.py
    feature_objects_set = set()
    for feature in settings.FEATURES:
        assert not isinstance(feature, Feature), f"The feature '{feature}' is " \
                                                 f"instantiated. Please redefine " \
                                                 f"this feature as only the reference " \
                                                 f"to the class, as shown in the docs. "

        feature_module_config = feature.split(".")
        feature_class_name = feature_module_config.pop()
        feature_module_name = ".".join(feature_module_config)
        feature_module = import_module(feature_module_name)
        feature_class = getattr(feature_module, feature_class_name)

        # Instantiate the feature class and traverse over its commands. Validate.
        feature_object = feature_class()
        assert issubclass(feature_class, Feature), f"'{feature_object.__class__.__name__}' " \
                                                   f"is not a subclass of 'Feature'. " \
                                                   f"Check your FEATURES list in " \
                                                   f"settings.py and verify that " \
                                                   f"all classes defined are Feature" \
                                                   f"subclasses."
        feature_objects_set.add(feature_object)

    assert len(feature_objects_set), "No features were provided in settings.py"

    # Instantiate router and provide the APP_NAME from settings
    message_router: AbstractMessageRouter = message_router_class(
        features=list(feature_objects_set),
        command_unknonw_responses=command_unknown_responses,
        help_keyword=help_keyword)

    # If devmode is active, return only one CliClient in a runner.
    if devmode:
        client = CliClient(message_router=message_router)
        return [Runner(settings.APP_NAME, client)]

    # Start the clients defined in settings.CLIENTS in separate threads
    for i, config in enumerate(settings.CLIENTS):
        try:
            module_config = config.pop("module").split(".")
            client_class_name = module_config.pop()
            module_name = ".".join(module_config)

            module = import_module(module_name)
            client_class = getattr(module, client_class_name)
        except Exception as e:
            raise NotImplementedError(f"Cannot use client at position {i}"
                                      f" due to incorrect config. Check "
                                      f"the following error and correct "
                                      f"any syntax error in settings.py:"
                                      f"\n{e}") from e

        # Provide the client with message_router and runner with client
        client = client_class(message_router=message_router, **config)
        runners.append(Runner(settings.APP_NAME, client))

        # Create a log entry for app start
        pyttman.logger.log(f" -- App {app_name} started: {datetime.now()} -- ")
    return runners
