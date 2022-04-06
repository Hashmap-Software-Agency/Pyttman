import os
import shutil
from pathlib import Path

import pyttman.tools.pyttmancli.intents as pyttman_cli_intents
from pyttman.core.containers import Message, Reply
from pyttman.tools.pyttmancli import PyttmanCli
from tests.core.entity_parsing.base import PyttmanInternalTestBaseCase


class TestPyttmanCLICreateAppIntent(PyttmanInternalTestBaseCase):
    test_intent_matching = True
    process_message = True
    ability_cls = PyttmanCli

    mock_message = Message("new app app_name")
    expected_entities = {"app_name": "app_name"}
    intent_class = pyttman_cli_intents.CreateNewApp
    intent_class.fail_gracefully = False

    def before_message_processing(self):
        stale_dir = Path(Path.cwd() / "app_name")
        if stale_dir.exists():
            shutil.rmtree(stale_dir)

    def after_message_processing(self):
        if Path("app_name").exists():
            shutil.rmtree("app_name")


class TestPyttmanCLIRunClientModeIntent(PyttmanInternalTestBaseCase):
    test_intent_matching = True
    process_message = True

    mock_message = Message("runclient app_name")
    expected_entities = {"app_name": "app_name"}
    intent_class = pyttman_cli_intents.RunAppInClientMode
    intent_class.fail_gracefully = True


class TestPyttmanCLIRunDevModeIntent(PyttmanInternalTestBaseCase):
    test_intent_matching = True
    process_message = True

    mock_message = Message("dev app_name")
    expected_entities = {"app_name": "app_name"}
    intent_class = pyttman_cli_intents.RunAppInDevMode
    intent_class.fail_gracefully = True


class TestPyttmanCLICreateAbility(PyttmanInternalTestBaseCase):
    test_intent_matching = True
    process_message = True
    expected_reply = Reply("Created ability 'musicplayer'.")

    mock_message = Message("new ability musicplayer app_name")
    expected_entities = {"app_name": "app_name",
                         "ability_name": "musicplayer"}
    intent_class = pyttman_cli_intents.CreateNewAbilityIntent
    intent_class.fail_gracefully = False

    def before_message_processing(self):
        if not Path("app_name").exists():
            os.mkdir("app_name")
        stale_dir = Path(Path.cwd() / "app_name" / "abilities" / "musicplayer")
        if stale_dir.exists():
            shutil.rmtree(stale_dir)

    def after_message_processing(self):
        if Path("app_name").exists():
            shutil.rmtree("app_name")
