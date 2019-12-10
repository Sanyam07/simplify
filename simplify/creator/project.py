"""
.. module:: siMpLify project
:synopsis: entry point for implementing multiple siMpLify steps
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass
import os
from typing import Any, Callable, Dict, Iterable, List, Optional, Union
import warnings

import numpy as np
import pandas as pd

import simplify.creator
from simplify.creator.codex import SimpleCodex
from simplify.creator.options import Options
from simplify.creator.outline import Outline
from simplify.library.utilities import listify
from simplify.creator.worker import Worker


@dataclass
class Project(SimpleCodex):
    """Controller class for siMpLify projects.

    Args:
        idea (Union[Idea, str]): an instance of Idea or a string containing the
            file path or file name (in the current working directory) where a
            file of a supported file type with settings for an Idea instance is
            located.
        filer (Optional[Union['Filer', str]]): an instance of filer or a string
            containing the full path of where the root folder should be located
            for file output. A filer instance contains all file path and
            import/export methods for use throughout the siMpLify package.
            Default is None.
        ingredients (Optional[Union['Ingredients', pd.DataFrame, pd.Series,
            np.ndarray, str]]): an instance of Ingredients, a string containing
            the full file path where a data file for a pandas DataFrame or
            Series is located, a string containing a file name in the default
            data folder, as defined in the shared Filer instance, a DataFrame, a
            Series, or numpy ndarray. If a DataFrame, ndarray, or string is
            provided, the resultant DataFrame is stored at the 'df' attribute
            in a new Ingredients instance. Default is None.
        name (Optional[str]): designates the name of the class used for internal
            referencing throughout siMpLify. If the class needs settings from
            the shared Idea instance, 'name' should match the appropriate
            section name in Idea. When subclassing, it is a good idea to use
            the same 'name' attribute as the base class for effective
            coordination between siMpLify classes. 'name' is used instead of
            __class__.__name__ to make such subclassing easier. If 'name' is not
            provided, __class__.__name__.lower() is used instead.
        steps (Optional[List[str], str]): ordered list of steps to
            use. Each step should match a key in 'options'. Defaults to
            None.
        options (Optional[Union['Options', Dict[str, Any]]]): allows setting of
            'options' property with an argument. Defaults to None.
        auto_publish (Optional[bool]): whether to call the 'publish' method when
            a subclass is instanced. For auto_publish to have an effect,
            'ingredients' must also be passed. Defaults to True.

    """
    idea: Union['Idea', str]
    filer: Optional[Union['Filer', str]] = None
    ingredients: Optional[Union[
        'Ingredients',
        pd.DataFrame,
        pd.Series,
        np.ndarray,
        str]] = None
    name: Optional[str] = 'simplify'
    steps: Optional[Union[List[str], str]] = None
    options: (Optional[Union['Options', Dict[str, Any]]]) = None
    auto_publish: Optional[bool] = True

    def __post_init__(self) -> None:
        """Initializes class attributes and calls appropriate methods."""
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Finalizes 'idea', 'filer', and 'ingredients instances.
        self.idea, self.filer, self.ingredients = simplify.startup(
            idea = self.idea,
            filer = self.filer,
            ingredients = self.ingredients)
        # Injects Options class with 'filer' and 'idea'.
        Options.idea = self.idea
        Options.filer = self.filer
        # Sets proxy property names.
        self.proxies = {'children': 'books'}
        super()._post_init__()
        return self

    """ Private Methods """

    def _draft_options(self) -> None:
        """Sets step options with information for module importation."""
        self.options = Options(
            options = {
                'farmer': Outline(
                    name = 'farmer',
                    module = 'simplify.farmer',
                    component = 'Almanac'),
                'chef': Outline(
                    name = 'chef',
                    module = 'simplify.chef',
                    component = 'Cookbook'),
                'actuary': Outline(
                    name = 'actuary',
                    module = 'simplify.actuary',
                    component = 'Ledger'),
                'critic': Outline(
                    name = 'critic',
                    module = 'simplify.critic',
                    component = 'Collection'),
                'artist': Outline(
                    name = 'artist',
                    module = 'simplify.artist',
                    component = 'Canvas')},
            codex = self)
        super()._draft_options()
        return self

    def _store_steps(self) -> None:
        """Stores all selected options in local attributes."""
        for step in self.steps:
            setattr(self, step, self.options[step])
        return self

    """ Core siMpLify Methods """

    def draft(self) -> None:
        """Sets initial attributes."""
        # Injects attributes from Idea instance, if values exist.
        self = self.idea.apply(instance = self)
        # Calls methods for setting 'options' and 'steps'.
        self._draft_options()
        self._draft_steps()
        self._store_steps()
        return self

    def publish(self, data: Optional[object] = None) -> None:
        """Finalizes steps by creating Book instances in options.

        Args:
            data (Optional[object]): an optional object needed for a Book's
                'publish' method.

        """
        if data is None:
            data = self.ingredients
        for step in self.steps:
            step.options.publish(
                author = self.author,
                steps = self.steps,
                data = data)
        self._store_steps()
        return self

    def apply(self, data: Optional[object] = None, **kwargs) -> None:
        """Applies created objects to passed 'data'.

        Args:
            data (Ingredients): data object for methods to be applied. This can
                be an Ingredients instance, but other compatible objects work
                as well.

        """
        if data is not None:
            self.ingredients = data
        for step in self.steps:
            self.ingredients = self.options.apply(
                worker = self.worker,
                key = step,
                data = self.ingredients,
                **kwargs)
        self._store_steps()
        return self