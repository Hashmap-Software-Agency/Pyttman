import typing
from itertools import zip_longest
from typing import Type, Dict, Union

from ordered_set import OrderedSet

from pyttman.core.containers import MessageMixin
from pyttman.core.entity_parsing.entity import Entity
from pyttman.core.entity_parsing.identifiers import Identifier
from pyttman.core.exceptions import InvalidPyttmanObjectException
from pyttman.core.mixins import PrettyReprMixin


class EntityFieldValueParser(PrettyReprMixin):
    """
    This class is used by EntityField classes primarily,
    as the inner-working engine for identifying and finding
    values which match the pattern provided in the declarative
    EntityParser Api component: 'EntityField'.
    """
    __repr_fields__ = ("identifier", "exclude", "prefixes", "suffixes")

    def __init__(self,
                 prefixes: tuple | typing.Callable = None,
                 suffixes: tuple | typing.Callable = None,
                 valid_strings: tuple | typing.Callable = None,
                 default:  typing.Any | typing.Callable = None,
                 span: int | typing.Callable = 0,
                 identifier: Type[Identifier] | None = None,
                 exclude: typing.Iterable[str] = None,
                 as_list: bool = False,
                 **kwargs):

        if hasattr(self, "value"):
            raise AttributeError("The field 'value' is reserved for internal "
                                 "use. Please choose a different name for "
                                 "the field.")

        self.truncates_message_in_parsing = True
        self.value = None
        self.case_preserved_cache = set()
        self.prefixes = prefixes or tuple()
        self.suffixes = suffixes or tuple()
        self.exclude = exclude or tuple()
        self.valid_strings = valid_strings or tuple()
        self.default = default if default is not None else None
        self.identifier = identifier
        self.span = span
        self.as_list = as_list
        self._properties_for_evaluation = {
            "prefixes": self.prefixes,
            "suffixes": self.suffixes,
            "span": self.span,
            "default": self.default,
            "valid_strings": self.valid_strings
        }

    def _prepare_params(self):
        """
        Prepares the arguments passed in the constructor.
        This happens after init in order to allow developers to provide
        callables as arguments, which should not be evaluated / executed
        at __init__ time due to the risk of DB connections not being
        established at that time.
        :return:
        """
        for name, value in self._properties_for_evaluation.items():
            if callable(value):
                try:
                    setattr(self, name, value())
                except Exception as e:
                    raise InvalidPyttmanObjectException(
                        "An error occurred during preparation of field "
                        f"'{name}' in '{self}'. If the callable takes "
                        f"arguments without provided defaults, consider "
                        f"using a partial.")

        # Validate that the object was constructed properly
        if not isinstance(self.prefixes, tuple) or \
                not isinstance(self.suffixes, tuple):
            raise AttributeError(f"'{self}' "
                                 f"is incorrectly configured: "
                                 f"'prefixes' and 'suffixes' "
                                 f"must be tuples.\nDo you have "
                                 f"a tuple with only one item? "
                                 f"Don't forget the trailing comma, "
                                 f"example: '(1,)' instead of '(1)'.")

        if self.valid_strings is not None and not isinstance(self.valid_strings, typing.Sequence):
            raise AttributeError("'valid_strings' must be a collection of "
                                 f"strings, got: '{self.valid_strings}'")
        else:
            self.valid_strings = tuple([i.casefold() for i in self.valid_strings])

    def reset(self) -> None:
        """
        Resets the parser, defaulting it's value to None.
        :return: None
        """
        self.value = None

    def parse_message(self, message: MessageMixin,
                      memoization: dict = None) -> None:
        """
        Walk the message and parse it for values.
        If the identified value exists in memoization,
        traverse on until value is returned or the
        message is exhausted.
        """
        self._prepare_params()
        if self.valid_strings:
            output = []
            word_index = 0

            casefolded_msg = message.lowered_content()
            common_occurrences = tuple(
                OrderedSet(casefolded_msg).intersection(self.valid_strings))

            for i, word in enumerate(common_occurrences):
                if i > self.span and not self.as_list:
                    break
                word_index = casefolded_msg.index(word)
                output.append(message.content[word_index])

            if len(output) > 1:
                self.value = Entity(output, index_in_message=word_index)
            elif len(output) == 1:
                self.value = Entity(output.pop())
            else:
                self.value = Entity(self.default, is_fallback_default=True)

            self._validate_prefixes_suffixes(message)

            if self.value:
                entity = self.value
                if entity.value == self.default:
                    return
                if isinstance(entity.value, list):
                    words_to_remove_from_message = entity.value
                    entity.index_in_message += len(entity.value)
                elif isinstance(entity.value, str):
                    words_to_remove_from_message = [entity.value]

                self._remove_words_from_message(message,
                                                *words_to_remove_from_message)
            return

        if self.truncates_message_in_parsing is False:
            return

        for i, _ in enumerate(message.content):
            parsed_entity: Entity = self._identify_value(message,
                                                         start_index=i)
            # An entity has been identified, and it's unique.
            if parsed_entity is not None and memoization.get(
                    parsed_entity.index_in_message) is None:
                self.value = parsed_entity
                break
            else:
                self.reset()

    def _remove_words_from_message_unless_default(self,
                                                  message,
                                                  *words_to_remove_from_message) -> None:
        """
        Removes elements from message.content, if they're present
        in the message, unless a word or other object happens to
        equal the 'self.default' property on the instance.
        """
        for word in words_to_remove_from_message:
            if word == self.default:
                continue
            try:
                message.content.remove(word)
            except ValueError:
                continue

    def _validate_message_with_affixes(self,
                                       affixes: tuple[str],
                                       message: MessageMixin,
                                       comparator: callable):
        entity = self.value
        if not (common_strings := set(affixes).intersection(message.content)):
            entity.value = self.default
            return
        for string in common_strings:
            if not comparator(message.content.index(string), entity.index_in_message):
                entity.value = self.default

    def _validate_prefixes_suffixes(self, message: MessageMixin):
        """
        Check 'prefixes' and 'suffixes' for Entity values to make sure
        that they comply
        :return:
        """
        if self.prefixes:
            self._validate_message_with_affixes(
                self.prefixes,
                message,
                lambda affix_index, value_index: affix_index < value_index)
        if self.suffixes:
            self._validate_message_with_affixes(
                self.suffixes,
                message,
                lambda affix_index, value_index: affix_index > value_index)

    def _identify_value(self, message: MessageMixin,
                        start_index: int = 0) -> Union[None, Entity]:
        """
        Parses the message for values to identify.

        Since the parser can be configured in many ways;
            * With suffixes only
            * With prefixes only
            * With prefixes and suffixes
            * With or without an Identifier class in all of the above

        ... these conditions need to be evaluated for each scenario.

        Pre- and Suffix tuples can contain strings or Parsers, or a
        combination. When EntityFieldValueParser instances are used in these tuples,
        their last occurring string, separated by spaces, is chosen
        as the ultimate prefix. This is so due to the fact that Parsers
        may span across multiple elements in the string collection
        and take ownership of more than one string in the sequence.

        If an Identifier is provided, it will try and find a value
        which complies with the pre- and suffixes as provided.
        If the Identifier is alone, it will return the first value
        encountered in the traversing of the message.

        :param message: Message object to parse
        :param start_index: Index pointer, where parsing
                            is started from in the message
        :return: Entity or None, depending on if parsing is successful.
        """
        prefix_entity = None
        suffix_entity = None
        prefixes = []
        suffixes = []
        prefix_indexes = []
        suffix_indexes = []
        last_prefix_index, earliest_suffix_index = 0, 0
        parsed_entity: Union[Entity, None] = None
        sanitized_msg_content = message.sanitized_content(preserve_case=False)

        # First - traverse over the pre- and suffixes and
        # collect them in separate lists
        for i_prefix, i_suffix in zip_longest(self.prefixes,
                                              self.suffixes,
                                              fillvalue=None):

            for rule, rule_collection in {i_prefix: prefixes,
                                          i_suffix: suffixes}.items():
                if rule is not None:
                    if isinstance(rule, EntityFieldValueParser) and rule.value is not None:
                        entity: Entity = rule.value
                        rule_collection.append(entity.value
                                               .split().pop().lower().strip())
                    elif isinstance(rule, str):
                        rule_collection.append(rule)

        for prefix, suffix in zip_longest(prefixes, suffixes, fillvalue=None):
            try:
                # Save the index of this prefix in the message
                if prefix is not None:
                    prefix_indexes.append(sanitized_msg_content.index(prefix))
                if suffix is not None:
                    suffix_indexes.append(sanitized_msg_content.index(suffix))
            except ValueError:
                # The prefix was not in the message
                continue

        # Let's extract the last occurring prefix,
        # and the earliest suffix of the ones present
        if len(prefixes):
            if not len(prefix_indexes):
                return None
            last_prefix_index = max(prefix_indexes)
            try:
                index_for_value = last_prefix_index + 1
                value_at_index = message.content[index_for_value]
                prefix_entity = Entity(value=value_at_index,
                                       index_in_message=index_for_value)
            except IndexError:
                prefix_entity = None
            start_index = last_prefix_index + 1

        if len(suffixes):
            if not len(suffix_indexes):
                return None

            earliest_suffix_index = min(suffix_indexes)
            try:
                index_for_value = earliest_suffix_index - 1
                value_at_index = message.content[index_for_value]
                suffix_entity = Entity(value=value_at_index,
                                       index_in_message=index_for_value)
            except IndexError:
                suffix_entity = None

        # If an Identifier was used - let it parse the message, but make
        # sure it complies with Pre- and/or suffix values, if configured
        if self.identifier is not None:
            identifier_object = self.identifier(start_index=start_index)
            identifier_entity = identifier_object .try_identify_entity(message)

            if identifier_entity is not None:
                allowed_scenarios = {
                    bool(not self.prefixes and not self.suffixes),

                    bool(self.prefixes and identifier_entity
                         .index_in_message >= (last_prefix_index + 1)),

                    bool(self.suffixes and identifier_entity.
                         index_in_message <= (earliest_suffix_index - 1)),

                    bool(self.prefixes and self.suffixes and
                         last_prefix_index < identifier_entity.
                         index_in_message < earliest_suffix_index)
                }

                if any(allowed_scenarios):
                    parsed_entity = identifier_entity
        else:
            if self.prefixes and not self.suffixes:
                parsed_entity = prefix_entity
            elif self.suffixes and not self.prefixes:
                parsed_entity = suffix_entity
            elif self.prefixes and self.suffixes:
                try:
                    begin = prefix_entity.index_in_message
                    end = suffix_entity.index_in_message
                    parsed_entity = Entity(
                        value=message.content[begin:end].pop(),
                        index_in_message=begin + 1)
                except IndexError:
                    parsed_entity = None

        # The ValueParser has no prefixes, suffixes or identifier.
        # The entity is the first string in the message.
        if not prefixes and not suffixes and not self.identifier:
            parsed_entity = Entity(value=message.content[0],
                                   index_in_message=0)

        # If the span property is set to greater than 0, walk further in
        # message.content and also include elements as far as the span
        # property designates.
        # If an identifier is used, it also has to approve of the string
        # for each span iteration as the walk in the message progresses.
        # If an Identifier is does not comply with a string, the walk is
        # cancelled.
        if parsed_entity is None:
            return parsed_entity

        while parsed_entity.value.casefold() in self.exclude:
            parsed_entity.index_in_message += 1
            # Traverse the message for as long as the current found
            # entity is in the 'exclude' tuple. If the end of message
            # is reached, quietly break the loop.
            try:
                parsed_entity.value = message.content[
                    parsed_entity.index_in_message]
            except IndexError:
                return None

        # Now, add words for as long as `span` allows us to iterate.
        for i in range(1, self.span):
            parsed_entity.index_in_message += 1
            try:
                if self.identifier:
                    identifier_object: Identifier = self.identifier(
                        start_index=parsed_entity.index_in_message)
                    # Identifier did not find
                    span_entity = identifier_object.try_identify_entity(
                        message)
                    if span_entity is None or span_entity.index_in_message != parsed_entity.index_in_message:
                        break
                    span_value = span_entity.value
                else:
                    span_value = message.content[parsed_entity.index_in_message]

            # There are not enough elements in message.content to walk
            # as far as the span property requests - abort.
            except IndexError:
                break
            else:
                if span_value not in self.exclude:
                    parsed_entity.value += f" {span_value}"
        return parsed_entity


def parse_entities(message: MessageMixin,
                   entity_fields: dict,
                   exclude: tuple = None) -> dict:
    """
    Traverse over all fields which are EntityFieldValueParser subclasses.
    Have them identify their values according to their
    constraints and conditions, and store them in a
    dictionary, returned at the end of parsing.
    :param exclude:
    :param entity_fields:
    :param message: MessageMixin subclass object to be parsed.
    :return:
    """
    output = {}
    if exclude is None:
        exclude = tuple()

    # The memoization dict is provided each EntityFieldValueParser instance
    # in order for them to avoid catching a string, previously
    # caught by a predecessor in iterations.
    parsers_memoization: Dict[int, Entity] = {}
    parser_joined_suffixes_and_prefixes: typing.Set[str] = set()

    for field_name, entity_field_instance in entity_fields.items():

        # Collect all parser pre- and suffixes
        parser_joined_suffixes_and_prefixes.update(
            entity_field_instance.prefixes + entity_field_instance.suffixes)

        # Share the 'exclude' tuple assigned by the developer in the
        # application code to each EntityFieldValueParser instance
        entity_field_instance.exclude = exclude
        entity_field_instance.parse_message(
            message,
            memoization=parsers_memoization)

        # See what the parser found - Entity or None.
        # Ignore entities in self.exclude.
        parsed_entity: Union[Entity, None] = entity_field_instance.value

        if parsed_entity is None or parsed_entity.value in exclude:
            # Use the developer declared fallback value (None, by default)
            output[field_name] = Entity(entity_field_instance.default,
                                        is_fallback_default=True)
        else:
            output[field_name] = parsed_entity

            # Store the entity for memoization to
            # prohibit multiple occurrences
            if entity_field_instance.truncates_message_in_parsing:
                parsers_memoization[
                    parsed_entity.index_in_message] = parsed_entity

    """
    Walk the message backwards and truncate entities which 
    contain elements from entities occurring later in the 
    message. 

    All elements in pre- and suffixes are also truncated 
    from all entities as they are delimiters, and should 
    not be present in the entity value.
    """
    duplicate_cache: typing.Set[str] = set(
        parser_joined_suffixes_and_prefixes)

    for field_name, entity in reversed(output.items()):
        entity_field = entity_fields.get(field_name)
        duplicate_cache.update(entity_field.case_preserved_cache)
        value_for_type_conversion = entity_field.default

        # Assess only Parsers which have successfully parsed entities.
        if entity.value is not None and entity.is_fallback_default is \
                False:
            # Value is a string - split the entity value by space,
            # so we can work with it
            try:
                split_value = entity.value.split()
            except AttributeError:
                split_value = entity.value

            # Truncate prefixes, suffixes and cached strings
            # from the entity
            if split_value != list(duplicate_cache):
                split_value = OrderedSet(split_value) \
                    .difference(duplicate_cache)

            duplicate_cache.update(split_value)
            duplicate_cache.update(set([i.casefold()
                                        for i in split_value]))
            value_for_type_conversion = str(" ").join(split_value)

        # New in 1.1.9 - If this is an EntityField class, convert
        # the value in the Entity with it.
        try:
            entity.value = entity_field.convert_value(
                value_for_type_conversion)
        except AttributeError:
            entity.value = value_for_type_conversion
        output[field_name] = entity
    return output


#   Backwards compatibility, Pyttman<=1.1.9.1
if __name__ != "__main__":
    ValueParser = EntityFieldValueParser
