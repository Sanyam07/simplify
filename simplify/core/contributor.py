"""
.. module:: contributor
:synopsis: algorithm and parameter content
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

import numpy as np
import pandas as pd
from scipy.stats import randint, uniform

from simplify.core.book import Page
from simplify.core.content import Outline
from simplify.core.content import Author
from simplify.core.content import SimpleDirector
from simplify.core.utilities import listify




@dataclass
class Algorithm(Author):
    """Finalizes an algorithm with parameters."""

    def __post_init__(self) -> None:
        super().__post_init__()
        return self

    """ Core siMpLify Methods """

    def draft(self) -> None:
        return self

    def publish(self, outline: 'Outline') -> None:
        """Finalizes parameter 'bunch'.

        Args:

        """
        self.process = getattr(import_module(outline.module), outline.algorithm)
        return self


@dataclass
class Parameters(Author):
    """Creates and stores parameter sets for Outlines.

    Args:
        idea ('Idea'): an instance of Idea with user settings.
        library ('Library'): an instance of Library with information about
            folder and file management.

    Attributes:
        bunch (dict): actual parameters dict. Returned by '__str__' and
            '__repr__' methods.

    """

    idea: 'Idea'
    library: 'Library'

    def __post_init__(self) -> None:
        super().__post_init__()
        return self

    """ Private Methods """

    def _build_idea(self, outline: 'Outline') -> None:
        """Acquires parameters from Idea instance.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        if (not hasattr(self, 'initial_parameters')
                or not self.initial_parameters):
            self.bunch = {}
            try:
                self.bunch.update(self.idea_parameters)
            except AttributeError:
                pass
        else:
             self.bunch = self.initial_parameters
        return self

    def _build_selected(self, outline: 'Outline') -> None:
        """Limits parameters to those appropriate to the outline.

        If 'outline.selected' is True, the keys from 'outline.defaults' are
        used to select the final returned parameters.

        If 'outline.selected' is a list of parameter keys, then only those
        parameters are selected for the final returned parameters.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        if outline.selected:
            if isinstance(outline.selected, list):
                parameters_to_use = outline.selected
            else:
                parameters_to_use = list(outline.default.keys())
            new_parameters = {}
            for key, value in self.bunch.items():
                if key in parameters_to_use:
                    new_parameters.update({key: value})
            self.bunch = new_parameters
        return self

    def _build_required(self, outline: 'Outline') -> None:
        """Adds required parameters (mandatory additions) to 'parameters'.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        try:
            self.bunch.update(outline.required)
        except TypeError:
            pass
        return self

    def _build_search(self, outline: 'Outline') -> None:
        """Separates variables with multiple options to search parameters.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        self.space = {}
        if outline.hyperparameter_search:
            new_parameters = {}
            for parameter, values in self.bunch.items():
                if isinstance(values, list):
                    if any(isinstance(i, float) for i in values):
                        self.space.update(
                            {parameter: uniform(values[0], values[1])})
                    elif any(isinstance(i, int) for i in values):
                        self.space.update(
                            {parameter: randint(values[0], values[1])})
                else:
                    new_parameters.update({parameter: values})
            self.bunch = new_parameters
        return self

    def _build_runtime(self,
            outline: 'Outline',
            page: 'Page') -> None:
        """Adds parameters that are determined at runtime.

        The primary example of a runtime parameter throughout siMpLify is the
        addition of a random seed for a consistent, replicable state.

        The runtime variables should be stored as attributes in the subclass so
        that the values listed in outline.runtimes match those attributes to
        be added to parameters.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        try:
            for key, value in outline.runtime.items():
                try:
                    self.bunch.update({key: getattr(page, value)})
                except AttributeError:
                    error = ' '.join('no matching runtime parameter',
                                     key, 'found in', page.name)
                    raise AttributeError(error)
        except (AttributeError, TypeError):
            pass
        return self

    def _build_conditional(self,
            outline: 'Outline',
            page: 'Page') -> None:
        """Modifies 'parameters' based upon various conditions.

        A page class should have its own '_build_conditional' method for this
        method to modify 'parameters'. That method should have a 'parameters'
        and 'page' (str) argument and return the modified 'parameters'.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        if outline.conditional:
            try:
                self.bunch = page._build_conditional(
                    page = outline.name,
                    parameters = self.bunch)
            except AttributeError:
                pass
        return self

    def _build_data_dependent(self,
            outline: 'Outline',
            ingredients: 'Ingredients') -> None:
        """Adds data-derived parameters to parameters 'bunch'.

        Args:
            outline (Outline): settings for parameters to be built.

        """
        try:
            for key, value in outline.data_dependents.items():
                self.bunch.update({key, getattr(ingredients, value)})
        except (KeyError, AttributeError):
            pass
        return self

    """ Core siMpLify Methods """

    def draft(self) -> None:
        """Declares parameter_types."""
        self.parameter_types = [
            'idea',
            'selected',
            'required',
            # 'search',
            'runtime',
            'conditional',
            'data_dependent']
        return self

    def publish(self,
            outline: 'Outline',
            ingredients: Optional['Ingredients'] = None,
            page: Optional['Page'] = None) -> None:
        """Finalizes parameter 'bunch'.

        Args:
            page ('Page'): page which contains a '_build_condtional'
                method, if applicable.
            ingredients ('Ingredients'): data container (Ingredients,
                Review, etc.)
                that has attributes matching any items stored in
                'outline.data_dependent'.

        """
        for parameter_type in self.parameter_types:
            if parameter_type in ['conditional', 'runtime']:
                getattr(self, '_'.join(['_get', parameter_type]))(
                    outline = outline,
                    page = page)
            elif parameter_type == 'data_dependent':
                getattr(self, '_'.join(['_get', parameter_type]))(
                    outline = outline,
                    data = ingredients)
            else:
                getattr(self, '_'.join(['_get', parameter_type]))(
                    outline = outline)
        return self