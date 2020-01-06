"""
.. module:: base
:synopsis: siMpLify base classes
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from abc import ABC
from abc import abstractmethod
from collections.abc import Collection
from collections.abc import Container
from collections.abc import MutableMapping
from collections.abc import MutableSequence
from dataclasses import dataclass
from dataclasses import field
from functools import update_wrapper
from functools import wraps
from importlib import import_module
from inspect import signature
from multiprocessing import Pool
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

from simplify.core.utilities import listify
from simplify.core.utilities import pathlibify


@dataclass
class SimpleOutline(Container):
    """Object construction instructions used by SimplePublisher instances.

    Ideally, this class should have no additional methods beyond the lazy
    loader ('load' method) and __contains__ dunder method.

    Users can use the idiom 'x in Option' to check if a particular attribute
    exists and is not None. This means default values for optional arguments
    should generally be set to None to allow use of that idiom.

    Args:
        name (str): designates the name of the class used for internal
            referencing throughout siMpLify. If the class needs settings from
            the shared Idea instance, 'name' should match the appropriate
            section name in Idea. When subclassing, it is a good idea to use
            the same 'name' attribute as the base class for effective
            coordination between siMpLify classes. 'name' is used instead of
            __class__.__name__ to make such subclassing easier.
        module (str): name of module where object to incorporate is located
            (can either be a siMpLify or non-siMpLify module).
        component (str): name of python object within 'module' to load.

    """
    name: str
    module: str
    component: str

    """ Required ABC Methods """

    def __contains__(self, attribute: str) -> bool:
        """Returns whether attribute exists in a subclass instance.

        Args:
            attribute (str): name of attribute to check.

        Returns:
            bool: whether the attribute exists and is not None.

        """
        return hasattr(self, attribute) and getattr(self, attribute) is not None

    """ Public Methods """

    def load(self) -> object:
        """Returns object from module based upon instance attributes.

        Returns:
            object from module indicated in passed Option instance.

        """
        return getattr(import_module(self.module), self.component)


@dataclass
class SimplePublisher(ABC):
    """Base class for creating Projects, Books, Chapters, and Pages."""

    def __post_init__(self) -> None:
        """ Sets initial attributes and calls 'draft' method."""
        if not hasattr(self, 'project') or self.project is None:
            self.project = self
        return self

    """ Private Methods """

    def _draft_idea(self, manuscript: 'SimpleManuscript') -> 'SimpleManuscript':
        """Drafts attributes from 'idea'.

        Args:
            manuscript ('SimpleManuscript'): 'SimpleManuscript' instance to be
                modified.

        Returns:
            manuscript ('SimpleManuscript': 'SimpleManuscript' instance with
                modifications made.

        """
        sections = ['general', manuscript.name]
        try:
            sections.extend(listify(manuscript.idea_sections))
        except AttributeError:
            pass
        for section in sections:
            try:
                for key, value in self.project.idea[section].items():
                    if not hasattr(manuscript, key):
                        setattr(manuscript, key, value)
            except KeyError:
                pass
        return manuscript

    def _publish_steps(self,
            manuscript: 'SimpleManuscript') -> 'SimpleManuscript':
        """Publishes 'steps' for 'manuscript'.

        Args:
            manuscript ('SimpleManuscript'): 'SimpleManuscript' instance to
                be modified.

        Returns:
            manuscript ('SimpleManuscript'): 'SimpleManuscript' instance
                with modifications made.

        """
        # Validates 'steps' or attempts to get 'steps' from 'idea'.
        if not manuscript.steps:
            try:
                manuscript.steps = listify(manuscript.project.idea[
                    manuscript.name]['_'.join([manuscript.name, 'steps'])])
            except KeyError:
                manuscript.steps = []
        return manuscript

    """ Core siMpLify Methods """

    @abstractmethod
    def draft(self, manuscript: 'SimpleManuscript') -> 'SimpleManuscript':
        """Subclasses must provide their own methods."""
        pass

    @abstractmethod
    def publish(self, manuscript: 'SimpleManuscript') -> 'SimpleManuscript':
        """Subclasses must provide their own methods."""
        pass


@dataclass
class SimpleManuscript(Collection):
    """Base class for Book, Chapter, and Page iterables."""

    def __post_init__(self) -> None:
        """Calls initialization methods and sets class instance defaults."""
        # Sets default 'name' attribute if none exists.
        if self.name is None:
            self.name = self.__class__.__name__.lower()
        # Automatically calls 'draft' method.
        try:
            self.draft()
        except AttributeError:
            pass
        # Calls 'publish' method if 'auto_publish' is True.
        if hasattr(self, 'auto_publish') and self.auto_publish:
            self.publish()
        # Calls 'apply' method if 'auto_apply' is True.
        if hasattr(self, 'auto_apply') and self.auto_apply:
            self.apply()
        return self

    """ Required ABC Methods """

    def __contains__(self, item: str) -> bool:
        """Returns whether 'attribute' exists in the class iterable.

        Args:
            item (str): name of item to check.

        Returns:
            bool: whether the 'item' exists in the class iterable.

        """
        return item in getattr(self, self.iterable)

    def __iter__(self) -> Iterable:
        """Returns class iterable."""
        return iter(getattr(self, self.iterable))

    def __len__(self) -> int:
        """Returns length of class iterable."""
        return len(getattr(self, self.iterable))


@dataclass
class SimpleOptions(MutableMapping, ABC):
    """Base class for storing options and strategies."""

    def __post_init__(self) -> None:
        """Initializes core attributes."""
        # Sets name of internal 'lexicon' dictionary.
        if not hasattr(self, 'lexicon'):
            self.lexicon = 'options'
        # Sets name of 'wilcards' which correspond to properties.
        if not hasattr(self, 'wildcards'):
            self.wildcards = ['default', 'all']
        return self

    """ Required ABC Methods """

    def __delitem__(self, item: str) -> None:
        """Deletes item in the 'lexicon' dictionary.

        Args:
            item (str): name of key in the 'lexicon' dictionary.

        """
        try:
            del getattr(self, self.lexicon)[item]
        except KeyError:
            pass
        return self

    def __getitem__(self, item: str) -> Any:
        """Returns item in the 'lexicon' dictionary.

        If there are no matches, the method searches for a matching wildcard in
        attributes.

        Args:
            item (str): name of key in the 'lexicon' dictionary.

        Returns:
            Any: item stored as a the 'lexicon' dictionary value.

        Raises:
            KeyError: if 'item' is not found in the 'lexicon' dictionary.

        """
        try:
            return getattr(self, self.lexicon)[item]
        except KeyError:
            if item in self.wildcards:
                return getattr(self, item)
            else:
                raise KeyError(' '.join(
                    [item, 'is not in', self.__class__,__.name__]))

    def __setitem__(self, item: str, value: Any) -> None:
        """Sets 'item' in the 'lexicon' dictionary to 'value'.

        Args:
            item (str): name of key in the 'lexicon' dictionary.
            value (Any): value to be paired with 'item' in the 'lexicon'
                dictionary.

        """
        getattr(self, self.lexicon)[item] = value
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of the 'lexicon' dictionary.

        Returns:
            Iterable stored in the 'lexicon' dictionary.

        """
        return iter(getattr(self, self.lexicon))

    def __len__(self) -> int:
        """Returns length of the 'lexicon' dictionary if 'iterable' not set..

        Returns:
            Integer of length of 'lexicon' dictionary.

        """
        return len(getattr(self, self.lexicon))

    """ Other Dunder Methods """

    def __add__(self, other: Union['SimpleContents', Dict[str, Any]]) -> None:
        """Combines argument with the 'lexicon' dictionary.

        Args:
            other (Union['SimpleContents', Dict[str, Any]]): another
                'SimpleContents' instance or compatible dictionary.

        """
        self.add(options = other)
        return self

    def __iadd__(self, other: Union['SimpleContents', Dict[str, Any]]) -> None:
        """Combines argument with the 'lexicon' dictionary.

        Args:
            other (Union['SimpleContents', Dict[str, Any]]): another
                'SimpleContents' instance or compatible dictionary.

        """
        self.add(options = other)
        return self

    """ Public Methods """

    def add(self,
            key: Optional[str] = None,
            value: Optional[Any] = None,
            options: Optional[Union[
                'SimpleContents', Dict[str, Any]]] = None) -> None:
        """Combines arguments with the 'lexicon' dictionary.

        Args:
            key (Optional[str]): dictionary key for 'value' to use. Defaults to
                None.
            value (Optional[Any]): item to store in the 'lexicon' dictionary.
                Defaults to None.
            options (Optional[Union['SimpleContents', Dict[str, Any]]]):
                another 'SimpleContents' instance or a compatible dictionary.
                Defaults to None.

        """
        if key is not None and value is not None:
            getattr(self, self.lexicon)[key] = value
        if options is not None:
            try:
                getattr(self, self.lexicon).update(
                    getattr(options, options.lexicon))
            except AttributeError:
                try:
                    getattr(self, self.lexicon).update(options)
                except (TypeError, AttributeError):
                    pass
        return self

    """ Wildcard Properties """

    @property
    def all(self) -> List[str]:
        """Returns list of keys of the 'lexicon' dictionary.

        Returns:
            List[str] of keys stored in the 'lexicon' dictionary.

        """
        return list(self.keys())

    @property
    def default(self) -> List[str]:
        """Returns '_default' or list of keys of the 'lexicon' dictionary.

        Returns:
            List[str] of keys stored in '_default' or the 'lexicon' dictionary.

        """
        try:
            return self._default
        except AttributeError:
            self._default = self.all
            return self._default

    @default.setter
    def default(self, options: Union[List[str], str]) -> None:
        """Sets '_default' to 'options'

        Args:
            'options' (Union[List[str], str]): list of keys in the lexicon
                dictionary to return when 'default' is accessed.

        """
        self._default = listify(options)
        return self

    @default.deleter
    def default(self, options: Union[List[str], str]) -> None:
        """Removes 'options' from '_default'.

        Args:
            'options' (Union[List[str], str]): list of keys in the lexicon
                dictionary to remove from '_default'.

        """
        for option in listify(options):
            try:
                del self._default[option]
            except KeyError:
                pass
            except AttributeError:
                self._default = self.all
                del self.default[options]
        return self


@dataclass
class SimpleContents(SimpleOptions):
    """Base class for storing options and strategies.

    Args:
        options (Optional[str, Any]): default stored dictionary. Defaults to an
            empty dictionary.
        null_value (Optional[Any]): value to return when 'none' is accessed.
            Defaults to None.

    """
    options: Optional[Dict[str, Any]] = field(default_factory = dict)
    null_value: Optional[Any] = None

    def __post_init__(self) -> None:
        """Sets name of internal 'lexicon' dictionary."""
        self.wildcards = ['default', 'all', 'none']
        super().__post_init__()
        return self

    """ Wildcard Properties """

    @property
    def none(self) -> None:
        """Returns 'null_value'.

        Returns:
            'null_value' attribute or None.

        """
        return self.null_value

    @none.setter
    def none(self, null_value: Any) -> None:
        """Sets 'none' to 'null_value'.

        Args:
            null_value (Any): value to return when 'none' is sought.

        """
        self.null_value = null_value
        return self
    

def SimpleConformer(ABC):
    """Base class decorator to convert arguments to proper types."""

    def __init__(self,
            callable: Callable,
            conformers: Optional[Dict[str, Callable]] = None) -> None:
        """Sets initial conformer options.

        Args:
            callable (Callable): wrapped method, function, or callable class.
            conformers Optional[Dict[str, Callable]]: keys are names of 
                parameters and values are functions to convert or validate 
                passed arguments. Those functions must return a completed
                object and take only a single passed passed argument. Defaults
                to None.

        """
        self.callable = callable
        update_wrapper(self, self.callable)
        if self.conformers is None:
            self.conformers = {}
        return self

    """ Required Wrapper Method """

    def __call__(self) -> Callable:
        """Converts arguments of 'callable' to appropriate type.

        Returns:
            Callable: with all arguments converted to appropriate types.

        """
        call_signature = signature(self.callable)
        @wraps(self.callable)
        def wrapper(self, *args, **kwargs):
            arguments = dict(call_signature.bind(*args, **kwargs).arguments)
            arguments = self.apply(arguments = arguments)
            return self.callable(self, **arguments)
        return wrapper

    """ Core siMpLify Methods """

    def apply(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Converts values of 'arguments' to proper types.
        
        Args:
            arguments (Dict[str, Any]): arguments with values to be converted.

        Returns:
            Dict[str, Any]: arguments with converted values.

        """
        for argument, conformer in self.conformers.items():
            try:
                arguments[argument] = conformer(arguments[argument])
            except KeyError:
                pass
        return arguments
    
    
@dataclass
class SimpleState(Container):
    """Base class for state management."""

    states: List[str]
    initial_state: Optional[str] = None

    def _post_init__(self) -> None:
        """Calls initialization methods and sets class instance defaults."""
        # Automatically calls 'draft' method.
        self.draft()
        return self

    """ Required ABC Methods """

    def __contains__(self, attribute: str) -> bool:
        """Returns whether 'attribute' exists in 'states'.

        Args:
            attribute (str): name of state to check.

        Returns:
            bool: whether the attribute exists in 'states'.

        """
        return attribute in self.states

    """ Other Dunder Methods """

    def __repr__(self) -> str:
        """Returns string name of 'state'."""
        return self.publish()

    def __str__(self) -> str:
        """Returns string name of 'state'."""
        return self.publish()

    """ State Management Methods """

    def change(self, new_state: str) -> None:
        """Changes 'state' to 'new_state'.

        Args:
            new_state(str): name of new state matching a string in 'states'.

        Raises:
            TypeError: if new_state is not in 'states'.

        """
        if new_state in self.states:
            self.previous = self.state
            self.state = new_state
        else:
            raise TypeError(' '.join([new_state, 'is not a recognized state']))

    """ Core siMpLify Methods """

    def draft(self) -> None:
        """Creates state machine default settings. """
        if self.initial_state:
            self.state = self.initial_state
        else:
            self.state = self.states[0]
        self.previous = self.state
        return self

    def publish(self) -> None:
        """Returns string name of 'state'."""
        return self.state


@dataclass
class SimpleDistributor(ABC):
    """Base class for siMpLify Importer and Exporter."""

    def __post_init__(self) -> None:
        """Calls initialization methods and sets class instance defaults."""
        self.draft()
        if self.auto_publish:
            self.publish()
        return self

    """ Private Methods """

    def _check_kwargs(self,
            variables_to_check: List[str],
            passed_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Selects kwargs for particular methods.

        If a needed argument was not passed, default values are used.

        Args:
            variables_to_check (List[str]): variables to check for values.
            passed_kwargs (Dict[str, Any]): kwargs passed to method.

        Returns:
            new_kwargs (Dict[str, Any]): kwargs with only relevant parameters.

        """
        new_kwargs = passed_kwargs
        for variable in variables_to_check:
            if not variable in passed_kwargs:
                if variable in self.default_kwargs:
                    new_kwargs.update(
                        {variable: self.inventory.default_kwargs[variable]})
                elif hasattr(self, variable):
                    new_kwargs.update({variable: getattr(self, variable)})
        return new_kwargs

    """ Core siMpLify Methods """

    def draft(self) -> None:
        self.library = SimpleContents(options = {
            'csv': 'csv',
            'matplotlib': 'mp',
            'pandas': 'pd',
            'pickle': 'pickle'})
        return self


@dataclass
class SimplePath(MutableMapping):
    """Base class for variable-state folder or file paths.

    Args:
        inventory ('Inventory): related Inventory instance.
        folder (str): folder where 'names' are or should be.
        names (Dict[str, str]): dictionary where keys are names of states and
            values are Path objects linked to those states.

    """
    inventory: 'Inventory'
    folder: str
    names: Dict[str, str]

    def __post_init__(self) -> None:
        """Calls initialization methods and sets class instance defaults."""
        # Automatically calls 'draft' method.
        self.draft()
        return self

    """ Required ABC Methods """

    def __delitem__(self, item: str) -> None:
        """Deletes item in 'names'.

        Args:
            item (str): name of key in 'names'.

        """
        try:
            del self.names[item]
        except KeyError:
            pass
        return self

    def __getitem__(self, item: str) -> Path:
        """Returns item in 'names'.

        Args:
            item (str): name of key in 'names'.

        Returns:
            Path: value stored as a 'names'.

        Raises:
            KeyError: if 'item' is not found in 'names'.

        """
        try:
            return self.names[item]
        except KeyError:
            raise KeyError(' '.join([item, 'is not in Inventory']))

    def __setitem__(self, item: str, value: Path) -> None:
        """Sets 'item' in 'names' to 'value'.

        Args:
            item (str): name of key in 'names'.
            value (Path): value to be paired with 'item' in 'names'.

        """
        self.names[item] = value
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of 'names'."""
        return iter(self.names)

    def __len__(self) -> int:
        """Returns length of 'names'."""
        return len(self.names)

    """ Other Dunder Methods """

    def __repr__(self) -> Path:
        """Returns value from 'names' based upon current 'state'."""
        return self.publish()

    def __str__(self) -> Path:
        """Returns value from 'names' based upon current 'state'."""
        return self.publish()

    """ Core siMpLify Methods """

    def draft(self) -> None:
        """Converts values in 'names' from str to Path objects."""
        new_names = {}
        for state, name in self.names.items():
            new_names[state] = pathlibify(path = folder.joinpath(name))
            if new_names[state].is_dir():
                self.inventory.create_folder(path = new_names[state])
        self.names = new_names
        return self

    def publish(self) -> Path:
        """Returns value from 'names' based upon current 'state'."""
        return self.names[self.inventory.state]


@dataclass
class SimpleType(MutableMapping):
    """Base class for proxy typing."""

    types: Dict[str, Any]

    def __post_init__(self) -> None:
        """Creates 'reversed_types' from passed 'types'."""
        self._create_reversed()
        return self

    """ Required ABC Methods """

    def __getitem__(self, key: str) -> Any:
        """Returns key in the 'types' or 'reverse_types' dictionary.

        Args:
            key (str): name of key to find.

        Returns:
            Any: value stored in 'types' or 'reverse_types' dictionaries.

        Raises:
            KeyError: if 'key' is neither found in 'types' nor 'reverse_types'
                dictionaries.

        """
        try:
            return self.types[key]
        except KeyError:
            try:
                return self.reverse_types[key]
            except KeyError:
                raise KeyError(' '.join(
                    [key, 'is not in', self.__class__,__.name__]))

    def __setitem__(self, key: str, value: Any) -> None:
        """Stoes arguments in 'types' and 'reverse_types' dictionaries.

        Args:
            key (str): name of key to set.
            value (Any): value tto be paired with key.

        """
        self.types[key] = value
        self.reverse_types[value] = key
        return self

    def __delitem__(self, key: str) -> None:
        """Deletes key in the 'types' and 'reverse_types' dictionaries.

        Args:
            key (str): name of key to find.

        """
        try:
            value = self.types[key]
            del self.types[key]
            del self.reverse_types[value]
        except KeyError:
            try:
                value = self.reverse_types[key]
                del self.reverse_types[key]
                del self.types[value]
            except KeyError:
                pass
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of the 'types' dictionary.

        Returns:
            Iterable stored in the 'types' dictionary.

        """
        return iter(self.types)

    def __len__(self) -> int:
        """Returns length of the 'types' dictionary if 'iterable' not set..

        Returns:
            int of length of 'types' dictionary.

        """
        return len(self.types)

    """ Private Methods """

    def _create_reversed(self) -> None:
        """Creates 'reversed_types'."""
        self.reversed_types = {value: key for key, value in self.types.items()}
        return self
