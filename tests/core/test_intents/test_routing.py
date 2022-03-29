from pyttman.core.ability import Ability
from pyttman.core.communication.models.containers import Message, ReplyStream, \
    Reply
from tests.core.entity_parsing.base import ImplementedTestIntent, \
    PyttmanInternalTestBaseCase


class IntentTwo(ImplementedTestIntent):
    """
    This test checks matching on a single word, only by the 'lead'
    property.
    """
    lead = ("new", "add")
    trail = ("expense", "purchase")
    ordered = True


class PyttmanIntentInternalEntityParserTestWebscraperApp(
    PyttmanInternalTestBaseCase
):

    class IntentClass(ImplementedTestIntent):
        """
        This test checks matching on a single word, only by the 'lead'
        property.
        """
        lead = ("new", "add")

    test_intent_matching = True
    mock_message = Message("add new purchase SomeItem 100")
