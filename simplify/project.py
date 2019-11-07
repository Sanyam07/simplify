"""
.. module:: siMpLify project
:synopsis: entry point for implementing siMpLify subpackages
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass
from importlib import import_module
import os
from typing import Any, Dict, Iterable, List, Union
import warnings

import numpy as np
import pandas as pd

from simplify import timer
from simplify.core.base import SimpleClass
from simplify.core.depot import Depot
from simplify.core.idea import Idea
from simplify.core.ingredients import Ingredients
from simplify.core.planner import SimplePlanner
from simplify.core.utilities import listify


@dataclass
class Project(SimplePlanner):
    """Controller class for siMpLify projects.

    Args:
        idea (Idea or str): an instance of Idea or a string containing the file
            path or file name (in the current working directory) where a
            supoorted settings file for an Idea instance is located. Once an
            Idea instance is createds, it is automatically an attribute to all
            other SimpleClass subclasses that are instanced in the future.
            Required.
        depot (Depot or str): an instance of Depot or a string containing the
            full path of where the root folder should be located for file
            output. A Depot instance contains all file path and import/export
            methods for use throughout the siMpLify package. Once a Depot
            instance is created, it is automatically an attribute of all other
            SimpleClass subclasses that are instanced in the future. Default is
            None.
        ingredients (Ingredients, DataFrame, Series, ndarray, or str): an
            instance of Ingredients, a string containing the full file path of
            where a data file for a pandas DataFrame or Series is located, a
            string containing a,file name in the default data folder, as defined
            in the shared Depot instance, a DataFrame, a Series, or numpy
            ndarray. If a DataFrame, ndarray, or string is provided, the
            resultant DataFrame is stored at the 'df' attribute in a new
            Ingredients instance. Default is None
        steps (List[str] or str): names of techniques to be applied. These
            names should match keys in the 'options' attribute. If using the
            Idea instance settings, this argument should not be passed. Default
            is None.
        name (str): designates the name of the class which should match the
            section of settings in the Idea instance and other methods
            throughout the siMpLify package. If subclassing siMpLify classes,
            it is often a good idea to maintain to the same 'name' attribute
            as the base class for effective coordination between siMpLify
            classes. Default is 'simple_package', but should be overwritten to
            match settings in the Idea instance.
            
    It is also a child class of SimpleClass and SimpleProject. So, its 
    documentation applies as well.

    """
    idea: Union[Idea, str]
    depot: Union[Depot, str, None] = None
    ingredients: Union[Ingredients, pd.DataFrame, pd.Series, np.ndarray, str,
                       None] = None
    steps: Union[List[str], str] = None
    name: str = 'simplify' 

    def __post_init__(self) -> None:
        super().__post_init__()
        return self

    def _draft_techniques(self) -> None:
        """Creates 'techniques' containing technique builder instances."""
        for step in listify(self.steps):
            try:
                instance = self._import_option(settings = self.options[step])()
                self.add_techniques(techniques = instance)
            except KeyError:
                error = ' '.join([step,
                                  'does not match an option in', self.name])
                raise KeyError(error)
        return self
    
    """ Core siMpLify Methods """

    def draft(self):
        # Sets step options with information for module importation.
        self.options = {
            'farmer': ('simplify.farmer', 'Almanac'),
            'chef': ('simplify.chef', 'Cookbook'),
            'actuary': ('simplify.actuary', 'Ledger'),
            'critic': ('simplify.critic', 'Review'),
            'artist': ('simplify.artist', 'Canvas')}
        # Sets parameters to be sent to each step's publish method.
        self.publish_parameters = {
            'farmer': (),
            'chef': ('ingredients'),
            'actuary': ('ingredients'),
            'critic': ('ingredients', 'chef.recipes'),
            'artist': ('ingredients', 'chef.recipes', 'critic.reviews')}
        super().draft()
        return self
