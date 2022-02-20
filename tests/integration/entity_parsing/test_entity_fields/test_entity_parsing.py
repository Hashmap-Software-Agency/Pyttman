from core.entity_parsing.fields import BoolEntityField
from pyttman.core.communication.models.containers import Message
from tests.integration.entity_parsing.base import PyttmanInternalTestCase, \
    ImplementedTestIntent
from tests.integration.entity_parsing.mockups import *


class PyttmanInternalEntityParserTestMusicPlayerApp(PyttmanInternalTestCase):
    mock_message = Message("Play 29 Palms by Robert Plant on Spotify or "
                           "soundCloud and shuffle songs")
    expected_entities = {
        "song": "29 Palms",
        "artist": "Robert Plant",
        "shuffle_songs": True,
        "platform_all": ["Spotify", "soundCloud"],
    }

    class IntentClass(ImplementedTestIntent):
        """
        Test a combination of custom Identifier class for a TextEntityField
        with valid_strings, message_contains all in combinations.
        """
        lead = ("play",)

        class EntityParser:
            exclude = ("on",)
            song = TextEntityField(span=5)
            artist = TextEntityField(prefixes=("by", "with"), span=10,
                                     identifier=CapitalizedIdentifier)

            shuffle_songs = BoolEntityField(message_contains=("shuffle",))

            # Test that both SoundCloud and Spotify are found despite being
            # misspelled in comparison to the mock message above
            platform_all = TextEntityField(as_list=True,
                                           valid_strings=("spOtifY",
                                                          "soundcloud"))


class PyttmanInternalEntityParserTestBookKeeperApp(PyttmanInternalTestCase):
    mock_message = Message("add expense Groceries at Whole Foods price 695,"
                           "5684")
    expected_entities = {
        "item": "Groceries",
        "store": "Whole Foods",
        "price": 695.5684,
        "some_undefined": "default"
    }

    class IntentClass(ImplementedTestIntent):
        """
        Tests the Text and Float EntityField classes and performs
        type assertion with prefixes and valid_strings with various
        case miss-matching
        """
        lead = ("new", "add")
        trail = ("expense", "purchase")

        class EntityParser:
            item = TextEntityField(valid_strings=("groceries", "clothes"))
            store = TextEntityField(prefixes=("in", "at", "on"), span=3)
            price = FloatEntityField(prefixes=("price",))
            some_undefined = TextEntityField(prefixes=("none",),
                                             default="default")


class PyttmanInternalEntityParserTestTranslatorApp(PyttmanInternalTestCase):
    mock_message = Message("Translate I Love You from english to swedish")
    expected_entities = {
        "text_to_translate": "I Love You",
        "from_language": "english",
        "to_language": "swedish"
    }

    class IntentClass(ImplementedTestIntent):
        """
        This test checks using an EntityField as a prefix.
        """
        lead = ("translate",)

        class EntityParser:
            exclude = ("to",)
            text_to_translate = TextEntityField(span=100)
            from_language = TextEntityField(prefixes=("from",))
            to_language = TextEntityField(prefixes=(from_language,))


class TestEntityParser(PyttmanInternalTestCase):
    mock_message = Message("add expense Clothes price 695,5684")
    expected_entities = {
        "item": "Clothes",
        "price": 695.5684
    }

    class IntentClass(ImplementedTestIntent):
        """
        This test checks The TextEntityField, and asserts that the 'default'
        argument works as expected.
        """
        lead = ("new", "add")
        trail = ("expense", "purchase")

        class EntityParser:
            item = TextEntityField(valid_strings=("food", "clothes"),
                                   default="default")
            price = FloatEntityField(prefixes=("price",))
