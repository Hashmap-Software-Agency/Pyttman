import shutil
from pathlib import Path

import pyttman.tools.pyttmancli.intents as pyttman_cli_intents
from pyttman.core.communication.models.containers import Message, Reply
from pyttman.tools.pyttmancli import PyttmanCli
from tests.core.entity_parsing.base import PyttmanInternalTestBaseCase


class TestPyttmanCLICreateAppIntent(PyttmanInternalTestBaseCase):
    test_intent_matching = True
    process_message = True
    ability_cls = PyttmanCli

    mock_message = Message("new app app_name")
    expected_entities = {"app_name": "app_name"}
    IntentClass = pyttman_cli_intents.CreateNewApp

#    def cleanup(self):
#        stale_dir = Path(Path.cwd() / "my_app_name")
#        if stale_dir.exists():
#            shutil.rmtree(stale_dir)


class TestPyttmanCLIRunClientModeIntent(PyttmanInternalTestBaseCase):
    test_intent_matching = True

    mock_message = Message("runclient app_name")
    expected_entities = {"app_name": "app_name"}
    IntentClass = pyttman_cli_intents.RunAppInClientMode


class TestPyttmanCLIRunDevModeIntent(PyttmanInternalTestBaseCase):
    test_intent_matching = True

    mock_message = Message("dev app_name")
    expected_entities = {"app_name": "app_name"}
    IntentClass = pyttman_cli_intents.RunAppInDevMode


class TestPyttmanCLICreateAbility(PyttmanInternalTestBaseCase):
    test_intent_matching = True
    process_message = True
    expected_reply = Reply("Created ability 'musicplayer'.")

    mock_message = Message("new ability musicplayer app_name")
    expected_entities = {"app_name": "app_name",
                         "ability_name": "musicplayer"}
    IntentClass = pyttman_cli_intents.CreateNewAbilityIntent

