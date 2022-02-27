from pyttman.core.communication.models.containers import Message
from tests.integration.entity_parsing.base import PyttmanInternalTestBaseCase, \
    ImplementedTestIntent


class PyttmanInternalEntityParserTestWebscraperApp(PyttmanInternalTestBaseCase):
    lead = ("search",)

    mock_message = Message("add new purchase SomeItem 100")

    class IntentClass(ImplementedTestIntent):
        """
        This test checks matching on a single word, only by the 'lead'
        property.
        """
        lead = ("new", "add")
        trail = ("expense", "purchase")
