#  MIT License
#
#  Copyright (c) 2021-present Simon Olofsson
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#   to deal in the Software without restriction, including without limitation
#   the rights to use, copy, modify, merge, publish, distribute, sublicense,
#   and/or sell copies of the Software, and to permit persons to whom the
#   Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#   in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.

from typing import Any, Sequence
from ordered_set import OrderedSet

from pyttman.core.exceptions import TypeConversionFailed
from pyttman.core.parsing.identifiers import IntegerIdentifier
from pyttman.core.parsing.parsers import ValueParser


class EntityFieldBase(ValueParser):
    type_cls = None
    identifier_cls = None

    def __init__(self, valid_strings: Sequence = None, **kwargs):
        super().__init__(identifier=self.identifier_cls, **kwargs)

        if valid_strings and isinstance(valid_strings, Sequence) is False:
            raise AttributeError("'valid_strings' must be a collection of "
                                 "strings")
        self.valid_strings = valid_strings

    def convert_value(self, value: Any) -> Any:
        """
        Try and convert the value passed, with the type associated
        with the class as 'type_cls'.

        :param value: Any
        :return: Any
        """
        if self.valid_strings:
            common = OrderedSet(self.valid_strings).intersection((value,))
            try:
                value = common.pop()
            except KeyError:
                value = None

        if value is not None:
            try:
                value = self.perform_type_conversion(value)
            except ValueError:
                raise TypeConversionFailed(from_type=type(value),
                                           to_type=self.type_cls)
        return value

    @classmethod
    def perform_type_conversion(cls, value: Any) -> Any:
        """
        Perform the conversion from unknown type in 'value
        with the logic and constraints known only by the
        subclass with knowledge about its typecast.

        :param value: Any
        :return: Any
        """
        return cls.type_cls(value)


class IntegerEntityField(EntityFieldBase):
    type_cls = int
    identifier_cls = IntegerIdentifier


class FloatEntityField(EntityFieldBase):
    type_cls = float
    identifier_cls = IntegerIdentifier

    @classmethod
    def perform_type_conversion(cls, value) -> Any:
        try:
            value = value.replace(",", ".")
        except AttributeError:
            pass
        return cls.type_cls(value)


class TextEntityField(EntityFieldBase):
    type_cls = str


class BoolEntityField(EntityFieldBase):
    type_cls = bool

