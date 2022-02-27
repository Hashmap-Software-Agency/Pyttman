import pyttman.tools.pyttmancli.intents as pyttman_cli_intents
from pyttman.core.communication.models.containers import Message
from tests.integration.entity_parsing.base import PyttmanInternalTestBaseCase


class TestPyttmanCLICreateApp(PyttmanInternalTestBaseCase):
    test_intent_matching = True

    mock_message = Message("new app my_app_name")
    expected_entities = {"app_name": "my_app_name"}
    IntentClass = pyttman_cli_intents.CreateNewApp


class TestPyttmanCLIRunClientMode(PyttmanInternalTestBaseCase):
    test_intent_matching = True

    mock_message = Message("runclient app_name")
    expected_entities = {"app_name": "app_name"}
    IntentClass = pyttman_cli_intents.RunAppInClientMode


class TestPyttmanCLIRunDevMode(PyttmanInternalTestBaseCase):
    test_intent_matching = True

    mock_message = Message("dev app_name")
    expected_entities = {"app_name": "app_name"}
    IntentClass = pyttman_cli_intents.RunAppInDevMode
