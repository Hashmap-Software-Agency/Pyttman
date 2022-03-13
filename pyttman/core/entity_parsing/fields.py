import inspect
from abc import ABC
from typing import Any, Sequence, Type

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
    type_cls = None
    identifier_cls = None

    def __init__(self,
                 identifier: Type[Identifier] | None = None,
                 as_list: bool = False,
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

        identifier_cls = self.identifier_cls
        self.as_list = as_list
        if identifier is not None:
            identifier_cls = identifier

        super().__init__(identifier=identifier_cls, **kwargs)

    def convert_value(self, value: Any) -> Any:
        """
        Try and convert the value passed, with the type associated
        with the class as 'type_cls'.

        :param value: Any
        :return: Any
        """
        try:
            value = self.perform_type_conversion(value)
        except Exception as e:
            raise TypeConversionFailed(from_type=type(value),
                                       to_type=self.type_cls) from e
        return value

    def perform_type_conversion(self, value: Any) -> Any:
        """
        Perform the conversion from unknown type in 'value
        with the logic and constraints known only by the
        subclass with knowledge about its typecast.

        :param value: Any
        :return: Any
        """
        if value is None:
            return value

        if self.as_list:
            if not isinstance(value, list):
                value_as_list = value.split()
            else:
                value_as_list = value

            for i, _ in enumerate(value_as_list):
                value_as_list[i] = self.type_cls(value_as_list[i])
            return value_as_list

        converted = self.type_cls(value)
        return converted


class IntegerEntityField(EntityFieldBase):
    """
    IntegerEntityField classes specialize in finding numbers.
    The value output type from this EntityField is <int>.
    """
    type_cls = int
    identifier_cls = IntegerIdentifier


class FloatEntityField(EntityFieldBase):
    """
    IntegerEntityField classes specialize in finding numbers.
    The value output type from this EntityField is <float>.
    """
    type_cls = float
    identifier_cls = IntegerIdentifier

    @classmethod
    def perform_type_conversion(cls, value) -> Any:
        if value is None:
            return 0.0
        try:
            value = value.replace(",", ".")
        except AttributeError:
            pass
        return cls.type_cls(value)


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
    truncates_message_in_parsing = False

    def __init__(self, *args,
                 message_contains: Sequence[str] = None,
                 **kwargs):
        super().__init__(*args, valid_strings=message_contains, **kwargs)

    def perform_type_conversion(self, value: Any) -> Any:
        """
        Perform the conversion from unknown type in 'value
        with the logic and constraints known only by the
        subclass with knowledge about its typecast.

        :param value: Any
        :return: Any
        """
        if self.as_list:
            value_as_list = value.split()
            for i, _ in enumerate(value_as_list):
                value_as_list[i] = self.type_cls(value_as_list[i])
            return value_as_list
        converted = self.type_cls(value)
        return converted
