"""
    This module contains parser objects used
    through out the Pyttman framework.

    Parsers are seen interacting with the
    Intent class as a configuration class
    to both identify which command matches
    a message, but also in ValueParser
    classes to add functionality for Command
    classes to identify values behind querystring
    intents which may be a value provider for a command.
"""
import abc
import typing
from abc import ABC
from itertools import zip_longest
from typing import Tuple, Any, Type, Collection, Dict, Optional, Union, List

from ordered_set import OrderedSet

from pyttman.core.communication.models.containers import MessageMixin
from pyttman.core.parsing.entity import Entity
from pyttman.core.parsing.identifiers import Identifier


class AbstractParser(abc.ABC):
    """
    Abstract Parser class
    """
    first_item = 0
    last_item = -1

    @abc.abstractmethod
    def parse_message(self, message: MessageMixin, memoization: dict = None) -> None:
        """
        Subclasses override this method, defining the
        logic for parsing the message contents and
        identifying the value of interest for each
        field in the EntityParser class in which
        these classes are created in as fields.
        """
        pass


class Parser(AbstractParser, ABC):
    """
    Base class for the Parser API in Pyttman.
    The various parsers in Pyttman inherit from this
    base class.
    Subclass this class when creating a custom Parser.

    field identifier:
        An optional Identifier class can be supplied as an Identifier.
        The Identifier's job is finding strings in a message which
        matches its own patterns.
    """
    identifier: Identifier = None
    exclude: Tuple = ()
    prefixes: Tuple = ()
    suffixes: Tuple = ()
    case_preserved_cache = set()

    def __init__(self, **kwargs):
        if hasattr(self, "value"):
            raise AttributeError("The field 'value' is reserved for internal use. "
                                 "Please choose a different name for the field.")
        self.value = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"exclude={self.exclude}, " \
               f"identifier={self.identifier}, " \
               f"value={self.value})"

    def reset(self) -> None:
        """
        Resets the parser, defaulting it's value to None.
        :return: None
        """
        self.value = None


class EntityParserBase(Parser):
    """
    The EntityParser class is designed to be used inside
    Intent classes, as an internal class.

    The EntityParser will, with it's defined fields,
    aid in identifying Entities (extracted information
    from user messages) and keep the entity values in
    the field variables themselves.
    """

    # EntityParser classes have Parser fields which help them
    # find entities in messages.
    parsers: Dict[str, Parser] = {}

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
               f"value={self.value}, " \
               f"exclude={self.exclude}, " \
               f"identifier={self.identifier}, " \
               f"parsers={self.parsers})"

    def parse_message(self, message: MessageMixin,
                      memoization: dict = None) -> None:
        """
        Traverse over all fields which are Parser subclasses.
        Have them identify their values according to their
        constraints and conditions, and store them in a
        dictionary, returned at the end of parsing.
        :param message: MessageMixin subclass object to be parsed.
        :param memoization:
        :return:
        """
        self.value = {}

        # The memoization dict is provided each Parser instance
        # in order for them to avoid catching a string, previously
        # caught by a predecessor in iterations.
        parsers_memoization: Dict[int, Entity] = {}
        parser_classes: Dict[str, Parser] = self.get_parsers()
        parser_joined_suffixes_and_prefixes: typing.Set[str] = set()

        for field_name, parser_object in parser_classes.items():

            # Collect all parser pre- and suffixes
            parser_joined_suffixes_and_prefixes.update(
                parser_object.prefixes + parser_object.suffixes)

            # Share the 'exclude' tuple assigned by the developer in the
            # application code to each Parser instance
            parser_object.exclude = self.exclude
            parser_object.parse_message(message,
                                        memoization=parsers_memoization)

            # See what the parser found - Entity or None.
            # Ignore entities in self.exclude.
            parsed_entity: Union[Entity, None] = parser_object.value

            if parsed_entity is None or parsed_entity.value in self.exclude:
                self.value[field_name] = None
            else:
                self.value[field_name] = parsed_entity

                # Store the entity for memoization to
                # prohibit multiple occurrences
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

        for field_name, entity in reversed(self.value.items()):
            iter_parser = self.parsers.get(field_name)
            duplicate_cache.update(iter_parser.case_preserved_cache)

            # Assess only Parsers which have successfully parsed entities.
            if entity is not None:
                # Work with OrderedSet's from ChoiceParsers with
                # 'multiple=True' differently.
                if isinstance(entity.value, OrderedSet):
                    duplicate_cache.update(entity.value)
                    duplicate_cache.update(set([i.casefold()
                                                for i in entity.value]))
                    self.value[field_name] = entity.value
                    continue

                # Value is a string - split the entity value by space
                # so we can work with it
                split_value = entity.value.split()

                # Truncate prefixes, suffixes and cached strings
                # from the entity
                if split_value != list(duplicate_cache):
                    split_value = OrderedSet(split_value)\
                        .difference(duplicate_cache)

                duplicate_cache.update(split_value)
                duplicate_cache.update(set([i.casefold()
                                            for i in split_value]))
                self.value[field_name] = str(" ").join(split_value)
            else:
                self.value[field_name] = None

    def get_parsers(self) -> Dict:
        """
        Returns a collection of fields on the instance of
        type Parser.
        :return: Tuple, instances of Parser.
        """
        parser_fields = {}

        for field_name in self.parsers:
            field_value = getattr(self, field_name)
            if not field_name.startswith("__") and \
                    issubclass(field_value.__class__, AbstractParser):
                parser_fields[field_name] = field_value
        return parser_fields

    @classmethod
    def from_meta_class(cls, metaclass):
        """
        Classmethod returning an instance of an EntityParser
        class with merged properties and fields from both
        classes.

        The EntityParser inner class inside an Intent subclass
        enables developers to easily parse for entities in
        messages from end users.

        The EntityParser is updated by merging the parser fields
        from the user defined EntityParser with the base class
        for EntityParser classes: 'EntityParserBase'.

        This omits the need for developers to use direct inheritance
        inside their Intent subclasses.

        This is performed by updating the __dict__ attribute of the
        user defined EntityClass with the EntityClassBase class.

        See PEP584 for details on the "|" operator for the union
        operator for dict updates.

        :param cls: Class reference for class method call
        :param metaclass: A User-defined EntityParser inner class
                          in an Intent subclass
        :return: EntityParserBase subclass instance
                 with merged __dict__ fields
        """
        user_defined_parsers = {name: parser for name, parser
                                in metaclass.__dict__.items()
                                if issubclass(parser.__class__,
                                              AbstractParser)}

        # Use the EntityParserBase as metaclass for an EntityParser class with
        # the fields configured in the user Intent.EntityParser class.
        merged_subclass = type(metaclass.__class__.__name__,
                               (EntityParserBase,),
                               {"parsers": user_defined_parsers})
        entity_parser_instance = merged_subclass()
        entity_parser_instance.__dict__ |= metaclass.__dict__
        entity_parser_instance.__dict__ |= user_defined_parsers
        return entity_parser_instance


class ValueParser(Parser):
    """
    Configuration class designed to be defined
    in a Intent. The ValueParser aids in identifying
    values provided by users in natural language.

    You can provide the ValueParser with a collection
    of prefixes and/or suffixes which will increasingly
    make the ValueParser more precise.

    You can also use an Identifier class, together with
    the prefixes and suffixes, or use it alone.

    An Identifier class will aid the parser further in
    finding the value of interest based on a regex match.

    Subclasses can add verbosity and define custom
    rules for how query string values are isolated
    and stored.

    If an identifier is specified without prefix and suffix,
    its value is saved as the ultimate value.

    If suffixes or prefixes or both are also defined,
    these must occur before and after the identifiers value, respectively.

    If suffix and prefix are defined together, they should
    be pointing to the same string, which is only logical.
    If so, that value is set as the ultimate value.

    If suffix or prefix are alone, their first encountered
    value is set as the ultimate value.

    example: `arrival_time = ValueParser(suffixes=("arrival", "arrive",
                                                   "arrives", "arrives"))`
              would return "20:44" on message "flight 34392 arrives 20:44"
    """

    def __init__(self, prefixes: Tuple = None, suffixes: Tuple = None,
                 identifier: Type[Identifier] = None, span: int = 0, **kwargs):
        super().__init__(**kwargs)

        if prefixes is None:
            prefixes = tuple()
        if suffixes is None:
            suffixes = tuple()

        self.prefixes = prefixes
        self.suffixes = suffixes
        self.identifier: Type[Identifier] = identifier
        self.span = span

        # Validate that the object was constructed properly
        if not isinstance(self.prefixes, tuple) or \
                not isinstance(self.suffixes, tuple):
            raise AttributeError("\n\nValueParser fields "
                                 "'prefixes' and 'suffixes' "
                                 f"must be tuples.\nDo you have "
                                 f"a tuple with only "
                                 f"one item? Don't forget "
                                 f"the trailing comma, "
                                 f"example: '(1,)' instead of '(1)'.")

    def __repr__(self):
        return f"{self.__class__.__name__}(value='{self.value}', " \
               f"identifier={self.identifier}, prefixes={self.prefixes}, " \
               f"suffixes={self.suffixes}, span={self.span})"

    def parse_message(self, message: MessageMixin,
                      memoization: dict = None) -> None:
        """
        Walk the message and parse it for values.
        If the identified value exists in memoization,
        traverse on until value is returned or the
        message is exhausted.
        """
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
        combination. When Parser instances are used in these tuples,
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
        prefix_entity, prefix_index, suffix_entity, suffix_index = None, None, None, None
        prefixes, suffixes, prefix_indexes, suffix_indexes = [], [], [], []
        last_prefix_index, earliest_suffix_index = 0, 0
        parsed_entity: Union[Entity, None] = None

        # First - traverse over the pre- and suffixes and
        # collect them in separate lists
        for i_prefix, i_suffix in zip_longest(
                self.prefixes, self.suffixes, fillvalue=None):
            if i_prefix is not None:
                if isinstance(i_prefix, Parser) and i_prefix.value is not None:
                    entity: Entity = i_prefix.value
                    prefixes.append(entity.value.split().pop().lower().strip())
                elif isinstance(i_prefix, str):
                    prefixes.append(i_prefix)

            if i_suffix is not None:
                if isinstance(i_suffix, Parser) and i_suffix.value is not None:
                    entity: Entity = i_suffix.value
                    suffixes.append(entity.value.split().pop().lower().strip())
                elif isinstance(i_suffix, str):
                    suffixes.append(i_suffix)

        # Ensure all indexing is non-case sensitive and without special characters
        lowered_content = message.sanitized_content(preserve_case=False)

        # Now, we store the indexes for all pre- and/or prefixes in separate lists too
        for prefix in prefixes:
            try:
                # Save the index of this prefix in the message
                prefix_indexes.append(lowered_content.index(prefix))
            except ValueError:
                # The prefix was not in the message - proceed
                continue

        for suffix in suffixes:
            try:
                suffix_indexes.append(lowered_content.index(suffix))
            except ValueError:
                continue

        # Let's extract the last occurring prefix,
        # and the earliest suffix of the ones present
        if prefixes:
            if not prefix_indexes:
                return None

            # Obtain the last occurrence of all prefixes
            last_prefix_index = max(prefix_indexes)
            try:
                prefix_entity = Entity(value=message.content[last_prefix_index + 1],
                                       index_in_message=last_prefix_index + 1)
            except IndexError:
                prefix_entity = None
            start_index = last_prefix_index + 1

        if suffixes:
            if not suffix_indexes:
                return None

            # Obtain the earliest occurring suffix
            earliest_suffix_index = min(suffix_indexes)
            try:
                suffix_entity = Entity(value=message.content[earliest_suffix_index - 1],
                                       index_in_message=earliest_suffix_index - 1)
            except IndexError:
                suffix_entity = None

        # If an Identifier was used - let it parse the message, but make sure it complies with
        # Pre- and/or suffix values, if configured

        if self.identifier:
            identifier_object = self.identifier(start_index=start_index)
            identifier_entity: Union[Entity, None] = identifier_object.try_identify_entity(message)
            if identifier_entity is not None:
                if any((not self.prefixes and not self.suffixes,
                       self.prefixes and identifier_entity.index_in_message >= (last_prefix_index + 1),
                       self.suffixes and identifier_entity.index_in_message <= (earliest_suffix_index - 1),
                       self.prefixes and self.suffixes and last_prefix_index
                       < identifier_entity.index_in_message < earliest_suffix_index)):
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
                    parsed_entity = Entity(value=message.content[begin:end].pop(), index_in_message=begin + 1)
                except IndexError:
                    parsed_entity = None

        # The ValueParser has no prefixes, suffixes or identifier.
        # The entity is the first string in the message.
        if not prefixes and not suffixes and not self.identifier:
            parsed_entity = Entity(value=message.content[0], index_in_message=0)

        # If the span property is set to greater than 0, walk further in
        # message.content and also include elements as far as the span
        # property designates.
        # If an identifier is used, it also has to approve of the string
        # for each span iteration as the walk in the message progresses.
        # If an Identifier is does not comply with a tring, the walk is
        # cancelled.
        if parsed_entity is not None and self.span:
            while parsed_entity.value.casefold() in self.exclude:
                parsed_entity.index_in_message += 1
                # Traverse the message for as long as the current found entity is
                # in the 'exclude' tuple. If the end of message is reached, quietly
                # break the loop.
                try:
                    parsed_entity.value = message.content[parsed_entity.index_in_message]
                except IndexError:
                    return None

            current_index = parsed_entity.index_in_message

            for i in range(1, self.span):
                try:
                    current_index += 1
                    if self.identifier:
                        identifier_object: Identifier = self.identifier(start_index=current_index)
                        # Identifier did not find
                        span_entity = identifier_object.try_identify_entity(message)
                        if span_entity is None or span_entity.index_in_message != current_index:
                            break
                        span_value = span_entity.value
                    else:
                        span_value = message.content[current_index]

                # There are not enough elements in message.content to walk as far as
                # the span property requests. Abort.
                except IndexError:
                    break
                else:
                    if span_value not in self.exclude:
                        parsed_entity.value += f" {span_value}"
        return parsed_entity


class PositionalParser(Parser):
    """
    The PositionalParser class is designed to be used
    when the position of a value in a message is known.
    Example: You know the user will provide the name
    of an airport as the last word in their message,
    every time. This can be a suitable occasion to
    use the PositionalParser and define the position
    of the expected value.
    """
    position = Parser.last_item

    def parse_message(self, message: MessageMixin, memoization: dict = None) -> None:
        """
        Set whichever element at index 'position'
        as value.
        :param memoization: An incrementing dictionary of previously added
                            input strings by other parsers
        :param message: Message object
        :return: None
        """
        try:
            self.value = Entity(value=message.content[self.position],
                                index_in_message=self.position)
        except IndexError:
            pass


class ChoiceParser(Parser):
    """
    The Choice Parser simplifies identifying a value
    in a message which matches a set of choices.

    A ChoiceParser is similar to an Enum in the way
    it constricts the valid options.

    An example is a virtual assistant who can order
    pizza. Since the menu is known, we can add the
    known kinds of pizza by name in the 'choices'
    field. The ChoiceParser will then find the matching
    element, if present.

    If multiple values are parsed by ChoiceParsers,
    one field per value has to be defined. Due to
    memoization when values are being parsed, no
    Parser class will parse the same value twice.

    :field choices: Tuple of strings which the Parser will
                    parse messages for
    :field multiple: bool, where the ChoiceParser will collect
                     multiple strings in an OrderedSet if set to
                     True. If False, only one parsed value is saved
                     in the Parser, even in scenarios where multiple
                     valid ones occur in the message.
    """

    def __init__(self, choices: Tuple, multiple: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.choices = choices
        self.multiple = multiple

    def parse_message(self, message: MessageMixin, memoization: dict = None) -> None:
        """
        Identify if any of the choices are present in the
        message.

        :param message: MessageMixin object from front end client
        :param memoization: An incrementing dictionary of previously added
                            input strings by other parsers
        :return: None
        """
        casefolded_choices = [i.casefold() for i in self._choices]
        sanitized_set = OrderedSet(message.sanitized_content(preserve_case=False))
        nonidentical_matching_strings = set()
        common_occurences = sanitized_set.intersection(casefolded_choices)

        if matching := list(common_occurences):
            for word in message.content:
                casefolded_word = word.casefold()
                if casefolded_word in matching and casefolded_word not in message.content:
                    nonidentical_matching_strings.add(word)

            self.case_preserved_cache.update(nonidentical_matching_strings)
            last_occurring_matching_entity = matching[-1]
            choice_position = casefolded_choices.index(last_occurring_matching_entity)
            position_in_message = sanitized_set.index(last_occurring_matching_entity)

            if not self.multiple:
                self.value = Entity(self._choices[choice_position], position_in_message)
            else:
                case_preserved = OrderedSet()
                while matching:
                    elem = matching.pop()
                    index_in_casefolded = casefolded_choices.index(elem)
                    case_preserved.add(self._choices[index_in_casefolded])
                self.value = Entity(case_preserved, position_in_message)

    @property
    def choices(self) -> Tuple[str]:
        return self._choices

    @choices.setter
    def choices(self, value: Tuple[str]) -> None:
        for i in value:
            if not isinstance(i, str):
                raise ValueError("All values in the 'choices' property must me 'str'")
            elif len(i.split()) > 1:
                raise ValueError(f"Spaces in Choices is not supported at this time: '{i}'")
        self._choices = tuple(value)
