import shutil
from pathlib import Path

import pyttman.tools.pyttmancli.intents as pyttman_cli_intents
from pyttman.core.communication.models.containers import Message
from tests.core.entity_parsing.base import PyttmanIntentInternalTestCase
from pyttman.tools.pyttmancli import PyttmanCli


class TestPyttmanCLICreateAppIntent(PyttmanIntentInternalTestCase):
    test_intent_matching = True
    test_entities = True
    ability_cls = PyttmanCli

    mock_message = Message("new app my_app_name")
    expected_entities = {"app_name": "my_app_name"}
    IntentClass = pyttman_cli_intents.CreateNewApp

    def cleanup(self):
        stale_dir = Path(Path.cwd() / "my_app_name")
        if stale_dir.exists():
            shutil.rmtree(stale_dir)


class TestPyttmanCLIRunClientModeIntent(PyttmanIntentInternalTestCase):
    test_intent_matching = True

    mock_message = Message("runclient app_name")
    expected_entities = {"app_name": "app_name"}
    IntentClass = pyttman_cli_intents.RunAppInClientMode


class TestPyttmanCLIRunDevModeIntent(PyttmanIntentInternalTestCase):
    test_intent_matching = True

    mock_message = Message("dev app_name")
    expected_entities = {"app_name": "app_name"}
    IntentClass = pyttman_cli_intents.RunAppInDevMode
