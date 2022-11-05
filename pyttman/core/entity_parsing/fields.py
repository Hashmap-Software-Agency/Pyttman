import inspect
from abc import ABC
from typing import Any, Sequence, Type

from pyttman.core.entity_parsing.entity import Entity

from pyttman.core.containers import MessageMixin, Message

from pyttman.core.entity_parsing.identifiers import IntegerIdentifier, \
    Identifier
from pyttman.core.entity_parsing.parsers import EntityFieldValueParser
from pyttman.core.exceptions import TypeConversionFailed, \
    InvalidPyttmanObjectException


class EntityFieldBase(EntityFieldValueParser, ABC):
    """
    EntityField classes make up the declarative API, to empower
    developers with a declarative and easy-to-use set of classes
    which specialize in identifying words or sentences in messages
    which match the given pattern.

    Not only to find the word(s) but also type-convert to a given
    datatype if a match is True.

    """
    default = None
    type_cls = None
    identifier_cls = None

    def __init__(self,
                 identifier: Type[Identifier] | None = None,
                 default: Any = None,
                 **kwargs):
        """
        :param as_list: If set to True combined with providing 'valid_strings',
                        the matched strings, if multiple, are stored as a list
                        rather than being a concatenated single string.

        :param identifier: Optional Identifier class. Provide an optional
               Identifier to further increase the granularity of the
               value you're looking for. Identifier classes can help in
               finding numbers, capitalized strings - or any other pattern
               by subclassing Identifier and defining your own regex pattern.
               A few common options are; CellphoneNumberIdentifier,
               CapitalizedIdentifier, and DateTimeStringIdentifier.
               You can read more about Identifier classes in the Pyttman
               documentation.
        """
        if self.type_cls is None or inspect.isclass(self.type_cls) is False:
            raise InvalidPyttmanObjectException("All EntityField classes "
                                                "must define a 'type_cls', "
                                                "and it must be a class, "
                                                "not an object or primitive. "
                                                f"'{self.type_cls}' is not "
                                                f"a valid value for "
                                                f"'type_cls'.")

        _default_arg = default if default is not None else self.default
        super().__init__(identifier=identifier or self.identifier_cls,
                         default=_default_arg, **kwargs)

    def convert_value(self, value: Any) -> Any:
        """
        Try and convert the value passed, with the type associated
        with the class as 'type_cls'.

        :param value: Any
        :return: Any
        """
        if value is None:
            return value

        try:
            if self.as_list:
                if not isinstance(value, list):
                    converted_as_list = value.split()
                else:
                    converted_as_list = value

                for i, _ in enumerate(converted_as_list):
                    current_item = converted_as_list[i]
                    custom_mutation = self.before_conversion(current_item)
                    converted_value = self.type_cls(custom_mutation)
                    converted_as_list[i] = converted_value
                return converted_as_list
            else:
                custom_mutation = self.before_conversion(value)
                converted_value = self.type_cls(custom_mutation)
        except Exception as e:
            raise TypeConversionFailed(from_type=type(value),
                                       to_type=self.type_cls) from e
        return converted_value

    def before_conversion(self, value: Any) -> str:
        """
        Perform the conversion from unknown type in 'value
        with the logic and constraints known only by the
        subclass with knowledge about its typecast.

        :param value: Any
        :return: Any
        """
        return value


class IntegerEntityField(EntityFieldBase):
    """
    IntegerEntityField classes specialize in finding numbers.
    The value output type from this EntityField is <int>.
    """
    type_cls = int
    identifier_cls = IntegerIdentifier

    def before_conversion(self, value: str) -> str:
        if isinstance(value, str):
            return "".join(i for i in value if i.isdigit())
        return value


class FloatEntityField(EntityFieldBase):
    """
    IntegerEntityField classes specialize in finding numbers.
    The value output type from this EntityField is <float>.
    """
    type_cls = float
    identifier_cls = IntegerIdentifier

    def before_conversion(self, value: str) -> str:
        converted = "".join(i for i in value if i.isdigit() or i in ".,")
        try:
            converted = converted.replace(",", ".")
        except AttributeError:
            pass
        return converted


class TextEntityField(EntityFieldBase):
    """
    TextEntityField classes specialize in finding text, of any kind.
    The value output type from this EntityField is <str>.
    """
    type_cls = str


class BoolEntityField(EntityFieldBase):
    """
    BoolEntityField will be set to True if a matching value is found
    in the Message. If no matching value is found, the value is set to
    False.
    The value output from this EntityField is <int>.
    """
    type_cls = bool
    default = False
    truncates_message_in_parsing = False

    def __init__(self, *args,
                 message_contains: Sequence[str] = None,
                 **kwargs):
        super().__init__(*args, valid_strings=message_contains, **kwargs)

    def parse_message(self,
                      message: MessageMixin,
                      original_message_content: tuple[str],
                      memoization: dict = None) -> None:
        original_content = Message(original_message_content).lowered_content()
        self.value = Entity(value=self.default, is_fallback_default=True)
        if set(self.valid_strings).intersection(original_content):
            self.value = Entity(value=True)


if __name__ != "__main__":
    StringEntityField = TextEntityField
    StrEntityField = TextEntityField
    IntEntityField = IntegerEntityField
