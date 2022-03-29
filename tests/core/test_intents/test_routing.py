from pyttman.core.ability import Ability
from pyttman.core.communication.models.containers import Message
from tests.core.entity_parsing.base import (
    PyttmanIntentInternalTestCase,
    ImplementedTestIntent
)


class IntentOne(ImplementedTestIntent):
    """
    This test checks matching on a single word, only by the 'lead'
    property.
    """
    lead = ("new", "add")


class IntentTwo(ImplementedTestIntent):
    """
    This test checks matching on a single word, only by the 'lead'
    property.
    """
    lead = ("new", "add")
    trail = ("expense", "purchase")
    ordered = True


class TestAbility(Ability):
    intents = (IntentOne, IntentTwo)


class PyttmanIntentInternalEntityParserTestWebscraperApp(
    PyttmanIntentInternalTestCase
):
    test_intent_matching = True
    mock_message = Message("add new purchase SomeItem 100")
    mock_intent_cls = IntentOne
