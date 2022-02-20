from core.communication.models.containers import Message
from core.entity_parsing.fields import TextEntityField, BoolEntityField
from tests.integration.entity_parsing.base import PyttmanInternalTestBaseCase, \
    ImplementedTestIntent


class PyttmanInternalEntityParserTestPyttmanCliCreate(
    PyttmanInternalTestBaseCase):
    mock_message = Message("new app my_app_name")
    expected_entities = {"app_name": "my_app_name"}

    class IntentClass(ImplementedTestIntent):
        """
        This tests the Pyttman CLI command for creating new apps.
        """
        lead = ("new",)
        trail = ("app",)
        ordered = True

        class EntityParser:
            app_name = TextEntityField()


class PyttmanInternalEntityParserTestPyttmanCliRunClient(PyttmanInternalTestBaseCase):
    mock_message = Message("run client app_name")
    expected_entities = {"app_name": "app_name"}

    class IntentClass(ImplementedTestIntent):
        """
        This tests the Pyttman CLI command for running apps.
        """
        lead = ("run",)
        trail = ("client",)
        ordered = True

        class EntityParser:
            app_name = TextEntityField()


class PyttmanInternalEntityParserTestPyttmanCliRunDev(PyttmanInternalTestBaseCase):
    mock_message = Message("run dev app_name")
    expected_entities = {"app_name": "app_name"}

    class IntentClass(ImplementedTestIntent):
        """
        This tests the Pyttman CLI command for running apps.
        """
        lead = ("run",)
        trail = ("dev",)
        ordered = True

        class EntityParser:
            app_name = TextEntityField()
