"""Core files for the siMplify package.

SimpleClass and SimpleType are parent abstract base classes that are used by
all classes (either directly or indirectly through other classes) in the
package.

Menu, Inventory, and Ingredients are three base classes that are used by every
project within the siMpLify framework.

FileType and DataType provide the default datatypes and file formats used. Both
contain dictionaries linking the proxy datatypes to python, numpy, and pandas
datatypes, as well as default values for those datatypes.

In addition, the timer decorator is included here and can be wrapped around any
class, method, or function.
"""
from abc import ABC, abstractmethod
from configparser import ConfigParser
import csv
from dataclasses import dataclass
from datetime import timedelta
from functools import wraps
import glob
from inspect import getfullargspec
import os
import pickle
import re
import time
from types import FunctionType
import warnings

import numpy as np
from numpy import datetime64
from pandas.api.types import CategoricalDtype
from more_itertools import unique_everseen
import pandas as pd
from tensorflow.test import is_gpu_available


@dataclass
class SimpleClass(ABC):
    """Absract base class for major classes in siMpLify package to support
    a common class structure and allow sharing of access methods.

    To use the class, a subclass must have the following methods:
        plan: a method which sets the default values for the
            subclass, and usually includes the self.options dictionary.
        prepare: a method which, after the user has set all options in the
            preferred manner, constructs the objects which can parse, modify,
            process, or analyze data.
    The following methods are not strictly required but should be used if
    the subclass is transforming data or other variable (as opposed to merely
    containing data or variables):
        perform: method which applies the prepared objects to passed data or
            other variables.

    To use the access dunder methods, the subclass should include self.options,
    a dictionary containing different strategies, algorithms, containers, or
    other objects.

    If the subclass includes boolean attributes of auto_prepare or auto_perform,
    and those attributes are set to True, then the prepare and/or perform methods
    are called when the class is instanced.
    """

    def __post_init__(self):
        # Removes various python warnings from console output.
        warnings.filterwarnings('ignore')
        # Creates menu attribute if string passed to menu when subclass was
        # instanced. Injects attributes from menu settings to subclass.
        if self.__class__.__name__ != 'Menu':
            self._check_menu()
        # Calls plan method to set up class instance defaults.
        self.plan()
        # Runs attribute checks from list in self.checks (if it exists).
        self._perform_checks()
        # Calls prepare method if it exists and auto_prepare is True.
        if hasattr(self, 'auto_prepare') and self.auto_prepare:
            self.prepare()
            # Calls perform method if it exists and auto_perform is True.
            if hasattr(self, 'auto_perform') and self.auto_perform:
                self.perform()
        return self

    """ Magic Methods """

    def __call__(self, menu, *args, **kwargs):
        """When called as a function, a subclass will return the perform method
        after running __post_init__. Any args and kwargs will only be passed
        to the perform method.

        Parameters:
            menu: an instance of Menu or path where a menu configuration file
                is located must be passed when a subclass is called as a
                function.
        """
        self.menu = menu
        self.auto_prepare = True
        self.auto_perform = False
        self.__post_init__()
        return self.perform(*args, **kwargs)

    def __contains__(self, item):
        """Checks if item is in self.options; returns boolean."""
        if item in self.options:
            return True
        else:
            return False

    def __delitem__(self, item):
        """Deletes item if in self.options or, if an instance attribute, it
        is assigned a value of None."""
        if item in self.options:
            del self.options[item]
        elif hasattr(self, item):
            setattr(self, item, None)
        else:
            error = item + ' is not in ' + self.__class__.__name__
            raise KeyError(error)
        return self

    def __getattr__(self, attr):
        """Returns dict methods applied to options attribute if those methods
        are sought from the class instance.

        Parameters:
            attr: attribute sought.
        """
        if attr in ['clear', 'items', 'pop', 'keys', 'update', 'values']:
            return getattr(self.options, attr)
        elif attr in self.__dict__:
            return self.__dict__[attr]
        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError
        else:
            return None

    def __getitem__(self, item):
        """Returns item if item is in self.options or is an atttribute."""
        if item in self.options:
            return self.options[item]
        elif hasattr(self, item):
            return getattr(self, item)
        else:
            return None

    def __iter__(self):
        """Returns options.items() to mirror dict functionality."""
        return self.options.items()

    def __setitem__(self, item, value):
        """Adds item and value to options dictionary."""
        self.options[item] = value
        return self

    """ Private Methods """

    def _check_gpu(self):
        """If gpu status is not set, checks if the local machine has a GPU
        capable of supporting included machine learning algorithms."""
        if hasattr(self, 'gpu'):
            if self.gpu and self.verbose:
                print('Using GPU')
            elif self.verbose:
                print('Using CPU')
        elif is_gpu_available:
            self.gpu = True
            if self.verbose:
                print('Using GPU')
        else:
            self.gpu = False
            if self.verbose:
                print('Using CPU')
        return self

    def _check_ingredients(self, ingredients = None):
        """Checks if ingredients attribute exists. If so, it determines if it
        contains a file folder, file path, or Ingredients instance. Depending
        upon its type, different actions are taken to actually create an
        Ingredients instance. If ingredients is None, then an Ingredients
        instance is created with no pandas DataFrames within it.

        Parameters:
            ingredients: an Ingredients instance, a file path containing a
                DataFrame or Series to add to an Ingredients instance, or
                a folder containing files to be used to compose Ingredients
                DataFrames and/or Series.
        """
        # Ingredients imported within function to avoid circular dependency.
        if ingredients:
            self.ingredients = ingredients
        if (isinstance(self.ingredients, pd.Series)
                or isinstance(self.ingredients, pd.DataFrame)):
            self.ingredients = Ingredients(df = self.ingredients)
        elif isinstance(self.ingredients, str):
            if os.path.isfile(self.ingredients):
                df = self.inventory.load(folder = self.inventory.data,
                                         file_name = self.ingredients)
                self.ingredients = Ingredients(df = df)
            elif os.path.isdir(self.ingredients):
                self.inventory.create_glob(folder = self.ingredients)
                self.ingredients = Ingredients()
        elif not self.ingredients:
            self.ingredients = Ingredients()
        return self

    def _check_inventory(self):
        """Adds an Inventory instance with default menu if one is not passed
        when subclass is instanced.
        """
        if not hasattr(self, 'inventory') or not self.inventory:
            # Inventory imported within function to avoid circular dependency.
            from simplify.core.inventory import Inventory
            self.inventory = Inventory(menu = self.menu)
        return self

    def _check_menu(self):
        """Loads menu from an .ini file if a string is passed to menu instead
        of a menu instance. Injects sections of menu to subclass instance
        using user settings stored in or default.
        """
        if hasattr(self, 'menu') and isinstance(self.menu, str):
            # Menu imported within function to avoid circular dependency.
            self.menu = menu.Menu(file_path = self.menu)
        # Adds attributes to class from appropriate sections of the menu.
        sections = ['general']
        if hasattr(self, 'menu_sections') and self.menu_sections:
            if isinstance(self.menu_sections, str):
                sections.append(self.menu_sections)
            else:
                sections.extend(self.menu_sections)
        if (hasattr(self, 'name')
                and self.name in self.menu.configuration
                and not self.name in sections):
            sections.append(self.name)
        print('sections', sections)
        self.menu.inject(instance = self, sections = sections)
        return self

    def _check_steps(self):
        """Checks for 'steps' attribute or finds an attribute with the class
        'name' prefix followed by 'steps' if 'steps' does not already exist or
        is None.
        """
        if not hasattr(self, 'steps') or not self.steps:
            if hasattr(self, self.name + '_steps'):
                if getattr(self, self.name + '_steps') in ['all', 'default']:
                    self.steps = list(self.options.keys())
                else:
                    self.steps = self.listify(getattr(
                        self, self.name + '_steps'))
            else:
                self.steps = []
        else:
            self.steps = self.listify(self.steps)
        if not hasattr(self, 'step') or not self.step:
            self.step = self.steps[0]
        return self

    def _perform_checks(self):
        """Checks attributes from self.checks and initializes them if they do
        not exist by calling the appropriate method. Those methods should
        have the prefix _check_ followed by the string in self.checks.
        """
        if hasattr(self, 'checks') and self.checks:
            for check in self.checks:
                getattr(self, '_check_' + check)()
        return self

    """ Public Methods """

    def conform(self, step):
        """Sets 'step' attribute to current step in siMpLify. This is used
        to maintain a universal state in the package for subclasses that are
        state dependent.
        """
        self.step = step
        return self

    @staticmethod
    def deduplicate(iterable):
        """Adds suffix to list, pandas dataframe, or pandas series."""
        if isinstance(iterable, list):
            return list(unique_everseen(iterable))
    # Needs implementation for pandas
        elif isinstance(iterable, pd.Series):
            return iterable
        elif isinstance(iterable, pd.DataFrame):
            return iterable

    @staticmethod
    def listify(variable):
        """Checks to see if the variable is stored in a list. If not, the
        variable is converted to a list or a list of 'none' is created if the
        variable is empty.
        """
        if not variable:
            return ['none']
        elif isinstance(variable, list):
            return variable
        else:
            return [variable]

    def load(self, name = None, file_path = None, folder = None,
             file_name = None, file_format = None):
        """Loads object from file into subclass attribute.

        Parameters:
            name: name of attribute for  file contents to be stored.
            file_path: a complete file path for the file to be loaded.
            folder: a path to the folder where the file should be loaded from
                (not used if file_path is passed).
            file_name: a string containing the name of the file to be loaded
                without the file extension (not used if file_path is passed).
            file_format: a string matching one the file formats in
                Inventory.extensions.
        """
        setattr(self, name, self.inventory.load(file_path = file_path,
                                                folder = folder,
                                                file_name = file_name,
                                                file_format = file_format))
        return self

    @abstractmethod
    def plan(self):
        """Required method that sets default values for a subclass.

        A dict called 'options' should be defined here for subclasses to use
        much of the functionality of SimpleClass.

        Generally, the 'checks' attribute should be set here if the subclass
        wants to make use of related methods.
        """
        pass
        return self

    @abstractmethod
    def prepare(self):
        """Required method which creates any objects to be applied to data or
        variables. In the case of iterative classes, such as Cookbook, this
        method should construct any plans to be later implemented by the
        'perform' method.
        """
        pass
        return self

    def perform(self, variable = None, **kwargs):
        """Optional method that implements all of the prepared objects on the
        passed variable. The variable is returned after being transformed by
        called methods.

        Parameters:
            variable: any variable. In most cases in the siMpLify package,
                variable is an instance of Ingredients. However, any variable
                or datatype can be used here.
            **kwargs: other parameters can be added to method as needed or
                **kwargs can be used.
        """
        pass
        return variable

    def save(self, variable = None, file_path = None, folder = None,
             file_name = None, file_format = None):
        """Exports a variable or attribute to disc.

        Parameters:
            variable: a python object or a string corresponding to a subclass
                attribute.
            file_path: a complete file path for the file to be saved.
            folder: a path to the folder where the file should be saved (not
                used if file_path is passed).
            file_name: a string containing the name of the file to be saved
                without the file extension (not used if file_path is passed).
            file_format: a string matching one the file formats in
                Inventory.extensions.
        """
        if isinstance(variable, str):
            variable = getattr(self, variable)
        self.inventory.save(variable = variable,
                            file_path = file_path,
                            folder = folder,
                            file_name = file_name,
                            file_format = file_format)
        return


@dataclass
class SimpleType(ABC):
    """Parent abstract base class for setting dictionaries related to datatypes
    and file types.

    To use the class, a subclass must have the following methods:
        plan: a method which sets the default values for the
            subclass. This method should define two dictionaries:
                name_to_type: a dict with strings as keys corresponding to
                    datatype values.
                default_values: a dict with strings as keys matching those in
                    'name_to_type' and default values for those datatypes.

    With those basic dictionaries, a reverse dictionary ('type_to_name') is
    created and a variety of dunder methods are implemented to make using the
    type structures easier.
    """

    def __post_init__(self):
        if hasattr(self, 'plan'):
            self.plan()
            self._create_reversed()
        return self

    """ Magic Methods """

    def __getattr__(self, attr):
        """Returns dict methods applied to 'name_to_type' attribute if those
        methods are sought from the class instance.

        Parameters:
            attr: attribute sought.
        """
        if attr in ['clear', 'items', 'pop', 'keys', 'update', 'values']:
            return getattr(self.name_to_type, attr)
        elif attr in self.__dict__:
            return self.__dict__[attr]
        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError
        else:
            return None

    def __getitem__(self, item):
        """Returns item if item is in 'name_to_type' or 'type_to_name'."""
        if item in self.name_to_type:
            return self.name_to_type[item]
        elif item in self.type_to_name:
            return self.type_to_name[item]
        else:
            error = item + ' is not in a recognized type.'
            raise KeyError(error)

    def __iter__(self):
        """Returns 'name_to_type.items()' to mirror dict functionality."""
        return self.name_to_type.items()

    def __setitem__(self, item, value):
        """Sets item to 'value' in 'name_to_type' and reverse in 'type_to_name'.
        If the class has 'default_values', then:
            if 'value' matches a 'key' in type_to_name, the same default value
            is applied. Otherwise, None is used as the default_value.
        """
        self.name_to_type.update({item : value})
        self.type_to_name.update({value : item})
        if hasattr(self, 'default_values'):
            if value in self.type_to_name:
                self.default_values.update({item : self.type_to_name[value]})
            else:
                self.default_values.update({item : None})
        return self

    """ Private Methods """

    def _create_reversed(self):
        """ Creates reversed dictionary of 'name_to_type' and stores it in
        'type_to_name'.
        """
        self.type_to_name = {
            value : key for key, value in self.name_to_type.items()}
        return self

    """ Public Methods """

    def keys(self):
        """Returns keys from 'name_to_type' to mirror dict functionality."""
        return self.name_to_type.keys()

    @abstractmethod
    def plan(self):
        """Required method that sets default values for a subclass."""
        pass
        return self

    def save(self):
        """Exports the subclass to disc in pickle format."""
        export_folder = getattr(self.inventory, self.export_folder)
        file_name = self.__class__.__name__.lower()
        self.inventory.save(variable = self,
                            folder = export_folder,
                            file_name = file_name,
                            file_format = 'pickle')
        return self

    def update(self, name, python_type, default_value = None):
        """Adds or replaces datatype with corresponding default value, if
        applicable.
        """
        self.type_to_name.update({name : python_type})
        self._create_reversed()
        if default_value and hasattr(self, 'default_values'):
            self.default_values.update({name : default_value})
        return self

    def values(self):
        """Returns values from 'name_to_type' to mirror dict functionality."""
        return self.name_to_type.values()


@dataclass
class DataTypes(SimpleType):
    """Stores dictionaries related to datatypes used by siMpLify package."""

    def __post_init__(self):
        super().__post_init__()
        return self

    def plan(self):
        """Sets default values related to datatypes."""
        # Sets string names of various datatypes available.
        self.name_to_type = {'boolean' : bool,
                             'float' : float,
                             'integer' : int,
                             'string' : object,
                             'categorical' : CategoricalDtype,
                             'list' : list,
                             'datetime' : datetime64,
                             'timedelta' : timedelta}
        # Sets default values for missing data based upon datatype of column.
        self.default_values = {'boolean' : False,
                               'float' : 0.0,
                               'integer' : 0,
                               'string' : '',
                               'categorical' : '',
                               'list' : [],
                               'datetime' : 1/1/1900,
                               'timedelta' : 0}
        return self

@dataclass
class FileTypes(SimpleType):
    """Stores dictionaries related to file types used by siMpLify package."""

    def __post_init__(self):
        super().__post_init__()
        return self

    def plan(self):
        """Sets default values related to filetypes."""
        # Sets string names of various datatypes available.
        self.name_to_type = {'csv' : '.csv',
                             'excel' : '.xlsx',
                             'feather' : '.ftr',
                             'h5' : '.hdf',
                             'hdf' : '.hdf',
                             'pickle' : '.pkl',
                             'png' : '.png',
                             'text' : '.txt',
                             'txt' : '.txt'}
        return self

@dataclass
class Menu(SimpleClass):
    """Loads and/or stores user settings.

    Menu creates a nested dictionary, converting dictionary values to
    appropriate data types, enabling nested dictionary lookups by user, and
    storing portions of the configuration dictionary as attributes in other
    classes. Menu is largely a wrapper for python's ConfigParser. It seeks
    to cure some of the most significant shortcomings of the base ConfigParser
    package:
        1) All values in ConfigParser are strings by default.
        2) The nested structure for getting items creates verbose code.
        3) It still uses OrderedDict (even though python 3.6+ has automatically
             orders regular dictionaries).

    To use the Menu class, the user can either:
        1) Pass file_path and the menu .ini file will automatically be loaded,
            or;
        2) Pass a prebuilt nested dictionary for storage in the Menu class.

    Whichever option is chosen, the nested menu dictionary is stored in the
    attribute .configuration. Users can store any key/value pairs in a section
    of the configuration dictionary as attributes in a class instance by using
    the inject method.

    If infer_types is set to True (the default option), the dictionary values
    are automatically converted to appropriate datatypes.

    For example, if the menu file (simplify_menu.ini stored in the appropriate
    folder) is as follows:

    [general]
    verbose = True
    file_type = csv

    [files]
    file_name = 'test_file'
    iterations = 4

    This code will create the menu file and store the general section as
    local attributes in the class:

        class FakeClass(object):

            def __init__(self):
                self.menu = Menu()
                self.menu.inject(instance = self, sections = ['general'])

    The result will be that an instance of Fakeclass will contain verbose and
    file_type as attributes that are appropriately typed.

    Because Menu uses ConfigParser, it only allows 2-level menu dictionaries.
    The desire for accessibility and simplicity dictated this limitation.

    Parameters:
        configuration: either a file path, file name, or two-level nested
            dictionary storing settings. If a file path is provided, A nested
            dict will automatically be created from the file and stored in
            'configuration'. If a file name is provided, Menu will look for it
            in the current working directory and store its contents in
            'configuration'.
        infer_types: boolean variable determines whether values in
            'configuration' are converted to other types (True) or left as
            strings (False).
        auto_prepare: sets whether to automatically call the 'prepare' method
            when the class is instanced. Unless adding a new source for
            configuration settings, this should be set to True.
        auto_perform: sets whether to automatically call the 'perform' method
            when the class is instanced. Unless adding a new source for
            configuration settings, this should be set to True.
    """
    configuration : object = None
    infer_types : bool = True
    auto_prepare : bool = True
    auto_perform : bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    def __delitem__(self, key):
        """Removes a dictionary section if name matches the name of a section.
        Otherwise, it will remove all entries with name inside the various
        sections of the configuration dictionary.

        Parameters:

            key: the name of the dictionary key or section to be deleted.
        """
        found_value = False
        if key in self.configuration:
            found_value = True
            self.configuration.pop(key)
        else:
            for config_key, config_value in self.configuration.items():
                if key in config_value:
                    found_value = True
                    self.configuration[config_key].pop(key)
        if not found_value:
            error_message = key + ' not found in menu dictionary'
            raise KeyError(error_message)
        return self

    def __getitem__(self, key):
        """Returns a section of the configuration dictionary or, if none is
        found, it looks at keys within sections. If no match is still found,
        it returns an empty dictionary.

        Parameters:

            key: the name of the dictionary key for which the value is
                sought.
        """
        found_value = False
        if key in self.configuration:
            found_value = True
            return self.configuration[key]
        else:
            for config_key, config_value in self.configuration.items():
                if key in config_value:
                    found_value = True
                    return self.configuration[config_key]
        if not found_value:
            return {}


    def __setitem__(self, section, nested_dict):
        """Creates a new subsection in a specified section of the configuration
        nested dictionary.

        Parameters:

            section: a string naming the section of the configuration
                dictionary.
            nested_dict: the dictionary to be placed in that section.
        """
        if isinstance(section, str):
            if isinstance(nested_dict, dict):
                self.configuration.update({section, nested_dict})
            else:
                error_message = 'nested_dict must be dict type'
                raise TypeError(error_message)
        else:
            error_message = 'section must be str type'
            raise TypeError(error_message)
        return self

    def __str__(self):
        """Returns the configuration dictionary."""
        return self.configuration

    def _check_configuration(self):
        """Checks the datatype of 'configuration' and sets 'technique' to
        properly prepare 'configuration'.
        """
        if self.configuration:
            if isinstance(self.configuration, str):
                if '.ini' in self.configuration:
                    self.technique = 'ini_file'
                elif '.py' in self.configuration:
                    self.technique = 'py_file'
                else:
                    error = 'configuration file must be .py or .ini file'
                    raise FileNotFoundError(error)
                if not os.path.isfile(os.path.abspath(self.configuration)):
                    self.configuration = os.path.join(os.getcwd(),
                                                      self.configuration)
            elif not isinstance(self.configuration, dict):
                error = 'configuration must be dict or file path'
                raise TypeError(error)
        else:
            error = 'configuration dict or path needed to instance Menu'
            raise AttributeError(error)
        return self

    def _create_from_ini(self):
        """Creates a configuration dictionary from an .ini file."""
        configuration = ConfigParser(dict_type = dict)
        configuration.optionxform = lambda option : option
        configuration.read(self.configuration)
        self.configuration = dict(configuration._sections)
        return self

    def _create_from_py(self):
        """Creates a configuration dictionary from an .py file."""
        pass
        return self

    def plan(self):
        """Loads configuration dictionary using ConfigParser if configuration
        does not presently exist.
        """
        # Lists tools from siMpLify package that should be added as local
        # staticmethods.
        self.tools = ['listify', 'typify']
        # Sets options for creating 'configuration'.
        self.options = {'py_file' : self._create_from_py,
                        'ini_file' : self._create_from_ini,
                        'dict' : None}
        return self

    def _infer_types(self):
        """If infer_types is True, all dictionary values in configuration are
        converted to the appropriate type.
        """
        if self.infer_types:
            for section, nested_dict in self.configuration.items():
                for key, value in nested_dict.items():
                    self.configuration[section][key] = self._typify(value)
        return self

    def _inject_base(self):
        """Injects parent class, SimpleClass with this Menu instance so that
        the instance is available to other files in the siMpLify package. It
        also adds the 'general' dictionary keys as attributes to SimpleClass.
        """
        SimpleClass.menu = self
        self.inject(instance = SimpleClass, sections = ['general'])
        return self

    def _typify(self, variable):
        """Converts strings to list (if ', ' is present), int, float, or
        boolean datatypes based upon the content of the string. If no
        alternative datatype is found, the variable is returned in its original
        form.
        """
        if ', ' in variable:
            return variable.split(', ')
        elif re.search('\d', variable):
            try:
                return int(variable)
            except ValueError:
                try:
                    return float(variable)
                except ValueError:
                    return variable
        elif variable in ['True', 'true', 'TRUE']:
            return True
        elif variable in ['False', 'false', 'FALSE']:
            return False
        elif variable in ['None', 'none', 'NONE']:
            return None
        else:
            return variable

    def inject(self, instance, sections, override = False):
        """Stores the section or sections of the configuration dictionary in
        the passed class instance as attributes to that class instance.

        Parameters:

            instance: either a class instance or class to which attributes
                should be added.
            sections: the sections of the configuration dictionary which should
                have items added as attributes to instance.
            override: if True, even existing attributes in instance will be
                replaced by configuration dictionary items.
        """
        for section in self.listify(sections):
            print(section)
            for key, value in self.configuration[section].items():
                if not hasattr(instance, key) or override:
                    setattr(instance, key, value)
                    print('attribute injected', getattr(instance, key))
        return

    def prepare(self):
        """Prepares instance of Menu by checking passed configuration parameter.
        """
        self._check_configuration()
        return self

    def perform(self):
        """Creates configuration setttings and injects Menu into SimpleClass.
        """
        if self.options[self.technique]:
            self.options[self.technique]()
        self._infer_types()
        self._inject_base()
        return self

    def update(self, new_settings):
        """Adds new settings to the configuration dictionary.

        Parameters:

           new_settings: can either be a dictionary or Menu object containing
               new attribute, value pairs or a string containing a file path
               from which new configuration options can be found.
        """
        if isinstance(new_settings, dict):
            self.configuration.update(new_settings)
        elif isinstance(new_settings, str):
            self.configuration.update(
                    self._create_configuration(file_path = new_settings))
        elif (hasattr(new_settings, 'configuration')
                and isinstance(new_settings.configuration, dict)):
            self.configuration.update(new_settings.configuration)
        else:
            error_message = 'new_options must be dict, Menu instance, or path'
            raise TypeError(error_message)
        return self



@dataclass
class Inventory(SimpleClass):
    """Creates and stores dynamic and static file paths and properly formats
    files for import and export.

    Parameters:

        root_folder: a string including the complete path from which the other
            paths and folders used by Inventory.
        data_folder: a string containing the data subfolder name or a complete
            path if the 'data_folder' is not off of 'root_folder'.
        results_folder: a string containing the results subfolder name or a
            complete path if the 'results_folder' is not off of 'root_folder'.
        datetime_naming: a boolean value setting whether the date and time
            should be used to create experiment subfolders (so that prior
            results are not overwritten).
        auto_prepare: sets whether to automatically call the 'prepare' method
            when the class is instanced. Unless making major changes to the
            file structure (beyond the 'root_folder', 'data_folder', and
            'results_folder' parameters), this should be set to True.
        auto_perform: sets whether to automatically call the 'perform' method
            when the class is instanced.
    """
    root_folder : str = ''
    data_folder : str = 'data'
    results_folder : str = 'results'
    datetime_naming : bool = True
    auto_prepare : bool = True
    auto_perform : bool = True

    def __post_init__(self):
        # Adds additional section of menu to be injected as local attributes.
        self.menu_sections = ['files']
        super().__post_init__()
        return self

    @property
    def file_in(self):
        if self.import_folder[self.step] in ['raw']:
            return self.folder_in
        else:
            return list(self.import_folder.keys())[list(
                    self.import_folder.keys()).index(self.step) - 1] + '_data'

    @property
    def file_out(self):
        if self.export_folder[self.step] in ['raw']:
            return self.folder_out
        else:
            return list(self.export_folder.keys())[list(
                    self.export_folder.keys()).index(self.step)] + '_data'

    @property
    def folder_in(self):
        return getattr(self, self.options[self.step])[0]

    @property
    def folder_out(self):
        return getattr(self, self.options[self.step])[1]

    @property
    def format_in(self):
        return self._get_file_format(io_status = 'import')

    @property
    def format_out(self):
        return self._get_file_format(io_status = 'export')

    @property
    def path_in(self):
        return self.create_path(io_status = 'import')

    @property
    def path_out(self):
        return self.create_path(io_status = 'export')

    def _add_branch(self, root_folder, subfolders):
        """Creates a branch of a folder tree and stores each folder name as
        a local variable containing the path to that folder.

        Parameters:
            root_folder: the folder from which the tree branch should be
                created.
            subfolders: a list of subfolder names forming the tree branch.
        """
        for subfolder in self.listify(subfolders):
            temp_folder = self.create_folder(folder = root_folder,
                                              subfolder = subfolder)
            setattr(self, subfolder, temp_folder)
            root_folder = temp_folder
        return self

    def _check_boolean_out(self, variable):
        """Either leaves boolean values as True/False or changes values to 1/0
        based on user settings.

        Parameters:
            variable: pandas DataFrame or Series with boolean output values.
        """
        # Checks whether True/False should be exported in data files. If
        # self.boolean_out is set to false, 1/0 are used instead.
        if hasattr(self, 'boolean_out') and self.boolean_out == False:
            variable.replace({True : 1, False : 0}, inplace = True)
        return variable

    def _check_encoding(self, encoding = None):
        """Checks value of local encoding variable. If not supplied, the
        method checks for a local variable. If neither option exists,
        the default value of 'windows-1252' is returned.

        Parameters:
            encoding: str variable containing file encoding technique that will
                be used for file importing.
        """
        if encoding:
            return encoding
        elif hasattr(self, 'file_encoding'):
            return self.file_encoding
        else:
            return 'windows-1252'

    def _check_file_name(self, file_name, io_status = None):
        """Checks passed file_name to see if it exists. If not, depending
        upon the io_status, a default file_name is returned.

        Parameters:
            file_name: string containing a file_name (without extension).
            io_status: either 'import' or 'export' based upon whether the user
                is seeking the appropriate file type based upon whether the
                file in question is being imported or exported.
        """
        if file_name:
            return file_name
        elif io_status == 'import':
            return self.file_in
        elif io_status == 'export':
            return self.file_out

    def _check_file_format(self, file_format = None, io_status = None):
        """Checks value of local file_format variable. If not supplied, the
        default from the Menu instance is used based upon whether import or
        export methods are being used. If the Menu options don't exist,
        '.csv' is returned.

        Parameters:
            file_format: string matching one of the supported file types in
                self.extensions.
            io_status: either 'import' or 'export' based upon whether the user
                is seeking the appropriate file type based upon whether the
                file in question is being imported or exported.
        """
        if file_format:
            return file_format
        elif io_status == 'import':
            return self.format_in
        elif io_status == 'export':
            return self.format_out
        else:
            return 'csv'

    def _check_float_format(self, float_format = None):
        """Checks value of local float_format variable. If not supplied, the
        method checks for a local variable. If neither option exists,
        the default value of '%.4f' is returned.

        Parameters:
            float_format: the desired format for exporting float numbers.
        """
        if float_format:
            return float_format
        elif hasattr(self, 'float_format'):
            return self.float_format
        else:
            return '%.4f'

    def _check_folder(self, folder, io_status = None):
        """Checks if folder is a full path or string matching an attribute.
        If no folder name is provided, a default value is used.

        Parameters:
            folder: a string either containing a folder path or the name of an
                attribute containing a folder path.
            io_status: either 'import' or 'export' based upon whether the user
                is seeking the appropriate file type based upon whether the
                file in question is being imported or exported.
        """
        if folder and os.path.isdir(folder):
            return folder
        elif folder and isinstance(folder, str):
            return getattr(self, folder)
        elif io_status == 'import':
            return self.folder_in
        elif io_status == 'export':
            return self.folder_out

    def _check_kwargs(self, variables_to_check, passed_kwargs):
        new_kwargs = passed_kwargs
        for variable in variables_to_check:
            if not variable in passed_kwargs:
                if variable in self.default_kwargs:
                    new_kwargs.update(
                            {variable : self.default_kwargs[variable]})
                elif hasattr(self, variable):
                    new_kwargs.update({variable : getattr(self, variable)})
        return new_kwargs

    def _check_root_folder(self):
        if self.root_folder:
            if os.path.isdir(self.root_folder):
                self.root = self.root_folder
            else:
                self.root = os.path.abspath(self.root_folder)
        else:
            self.root = os.path.join('..', '..')
        return self

    def _check_test_data(self, test_data = False, test_rows = None):
        """Checks value of local test_data variable. If not supplied, the
        default from the Menu instance is used. If not selected, 'None' is
        returned because that prevents the parameter from being activated
        using pandas methods.

        Parameters:
            test_data: boolean variable indicating whether a test sample should
                be used. If set to False, the full dataset is imported.
            test_rows: an integer containing the size of the test sample.
        """
        if not test_data:
            return None
        elif not test_data and not self.test_data:
            return None
        else:
            if not test_rows:
                test_rows = self.test_rows
            return test_rows

    def plan(self):
        """Creates data, results, and experiment folders based upon passed
        parameters. The experiment folder name is based upon the date and time
        to avoid overwriting previous experiments unless datetime_naming is set
        to False. If False, a default folder named 'experiment' will be used.
        Also, creates a dictionary for file_format names and extensions.
        """
        self.tools = ['listify']
        self.extensions = FileTypes()
        self.data_subfolders = ['raw', 'interim', 'processed', 'external']
        self.default_kwargs = {'index' : False,
                               'header' : None,
                               'low_memory' : False,
                               'dialect' : 'excel',
                               'usecols' : None,
                               'columns' : None,
                               'nrows' : None,
                               'index_col' : False}
        self.options = {'sow' : ['raw', 'raw'],
                        'reap' : ['raw', 'interim'],
                        'clean' : ['interim', 'interim'],
                        'bundle' : ['interim', 'interim'],
                        'deliver' : ['interim', 'processed'],
                        'cook' : ['processed', 'processed']}
        self.options_index = {'import' : 0,
                              'export' : 1}
        return self

    def _get_file_format(self, io_status):
        if (self.options[self.step][self.options_index[io_status]]
                in ['raw']):
            return self.source_format
        elif (self.options[self.step][self.options_index[io_status]]
                in ['interim']):
            return self.interim_format
        elif (self.options[self.step][self.options_index[io_status]]
                in ['processed']):
            return self.final_format

    def _inject_base(self):
        """Injects parent class, SimpleClass with this Inventory instance so
        that the instance is available to other files in the siMpLify package.
        """
        SimpleClass.inventory = self
        return self

    def _load_csv(self, file_path, **kwargs):
        """Loads csv file into a pandas DataFrame."""
        additional_kwargs = ['encoding', 'index_col', 'header', 'usecols',
                             'low_memory']
        kwargs = self._check_kwargs(variables_to_check = additional_kwargs,
                                    passed_kwargs = kwargs)
        if self.test_data and not 'chunksize' in kwargs:
            kwargs.update({'nrows' : self.test_chunk})
        variable = pd.read_csv(file_path, **kwargs)
        return variable

    def _load_excel(self, file_path, **kwargs):
        additional_kwargs = ['index_col', 'header', 'usecols']
        kwargs = self._check_kwargs(variables_to_check = additional_kwargs,
                                    passed_kwargs = kwargs)
        if self.test_data and not 'chunksize' in kwargs:
            kwargs.update({'nrows' : self.test_chunk})
        variable = pd.read_excel(file_path, **kwargs)
        return variable

    def _load_feather(self, file_path, **kwargs):
        """Loads feather file into pandas DataFrame."""
        return pd.read_feather(file_path, nthreads = -1, **kwargs)

    def _load_h5(self, file_path, **kwargs):
        return self._load_hdf(file_path, **kwargs)

    def _load_hdf(self, file_path, **kwargs):
        """Loads hdf5 file into pandas DataFrame."""
        additional_kwargs = ['columns']
        kwargs = self._check_kwargs(variables_to_check = additional_kwargs,
                                    passed_kwargs = kwargs)
        if self.test_data and not 'chunksize' in kwargs:
            kwargs.update({'chunksize' : self.test_rows})
        if 'usecols' in kwargs:
            kwargs.update({'columns' : kwargs['usecols']})
            kwargs.pop('usecols')
        return pd.read_hdf(file_path, **kwargs)

    def _load_json(self, file_path, **kwargs):
        """Loads json file into pandas DataFrame."""
        additional_kwargs = ['encoding', 'columns']
        kwargs = self._check_kwargs(variables_to_check = additional_kwargs,
                                    passed_kwargs = kwargs)
        if self.test_data and not 'chunksize' in kwargs:
            kwargs.update({'chunksize' : self.test_rows})
        if 'usecols' in kwargs:
            kwargs.update({'columns' : kwargs['usecols']})
            kwargs.pop('usecols')
        return pd.read_json(file_path = file_path, **kwargs)

    def _load_pickle(self, file_path, **kwargs):
        """Returns an unpickled python object."""
        return pickle.load(open(file_path, 'rb'))

    def _load_png(self, file_path, **kwargs):
        error = 'loading .png files is not supported'
        raise NotImplementedError(error)

    def _load_text(self, file_path, **kwargs):
        return self._load_txt(file_path = file_path, **kwargs)

    def _load_txt(self, file_path, **kwargs):
        with open(file_path, mode = 'r', errors = 'ignore',
                  encoding = self.file_encoding) as a_file:
            return a_file.read()

    def _make_folder(self, folder):
        """Creates folder if it doesn't already exist.

        Parameters:
            folder: a string containing the path of the folder.
        """
        if not os.path.exists(folder):
             os.makedirs(folder)
        return self

    def _save_csv(self, variable, file_path, **kwargs):
        if isinstance(variable, pd.DataFrame):
            additional_kwargs = ['index', 'header', 'encoding', 'float_format']
            kwargs = self._check_kwargs(variables_to_check = additional_kwargs,
                                        passed_kwargs = kwargs)
            variable.to_csv(file_path, **kwargs)
        elif isinstance(variable, pd.Series):
            self.writer.writerow(variable)
        return

    def _save_excel(self, variable, file_path, **kwargs):
        if isinstance(variable, pd.DataFrame):
            additional_kwargs = ['index', 'header', 'encoding', 'float_format']
            kwargs = self._check_kwargs(variables_to_check = additional_kwargs,
                                        passed_kwargs = kwargs)
            variable.excel(file_path, **kwargs)
        elif isinstance(variable, pd.Series):
            self.writer.writerow(variable)
        return

    def _save_feather(self, variable, file_path, **kwargs):
        variable.reset_index(inplace = True)
        variable.to_feather(file_path, **kwargs)
        return

    def _save_h5(self, variable, file_path, **kwargs):
        variable.to_hdf(file_path, **kwargs)
        return

    def _save_hdf(self, variable, file_path, **kwargs):
        variable.to_hdf(file_path, **kwargs)
        return

    def _save_json(self, variable, file_path, **kwargs):
        variable.to_json(file_path, **kwargs)
        return

    def _save_pickle(self, variable, file_path, **kwargs):
        """Pickles python object."""
        pickle.dump(variable, open(file_path, 'wb'))
        return

    def _save_png(self, variable, file_path, **kwargs):
        variable.savefig(file_path, bbox_inches = 'tight')
        variable.close()
        return

    def add_file_format(self, file_format, extension, load_method,
                        save_method):
        """Adds or replaces a file extension option.

        Parameters:
            file_format: string name of the file_format.
            extension: file extension (without period) to be used.
            load_method: a method to be used when loading files of the passed
                file_format.
            save_method: a method to be used when saving files of the passed
                file_format.
        """
        self.extensions.update({file_format : extension})
        if isinstance(load_method, str):
            setattr(self, '_load_' + file_format, '_load_' + load_method)
        else:
            setattr(self, '_load_' + file_format, load_method)
        if isinstance(save_method, str):
            setattr(self, '_save_' + file_format, '_save_' + save_method)
        else:
            setattr(self, '_save_' + file_format, save_method)
        return self

    def add_folders(self, root_folder, subfolders):
        """Adds a list of subfolders to an existing root_folder.

        Parameters:
            root_folder: path of folder where subfolders should be created.
            subfolders: list of subfolder names to be created.
        """
        for subfolder in self.listify(subfolders):
            temp_folder = self.create_folder(folder = root_folder,
                                              subfolder = subfolder)
            setattr(self, subfolder, temp_folder)
        return self

    def add_tree(self, folder_tree):
        """Adds a folder tree to disc with corresponding attributes to the
        Inventory instance.

        Parameters:
            folder_tree: a dictionary containing a folder tree to be created
                with corresponding attributes to the Inventory instance.
        """
        for folder, subfolders in folder_tree.items():
            self._add_branch(root_folder = folder,
                             subfolders = subfolders)
        return self

    def create_batch(self, folder = None, file_format = None,
                    include_subfolders = True):
        """Creates a list of paths in the self.data_in folder based upon
        file_format. If recursive is True, subfolders are searched as well for
        matching file_format files.
        """
        folder = self._check_folder(folder = folder)
        file_format = self._check_file_format(file_format = file_format,
                                              io_status = 'import')
        extension = self.extensions[file_format]
        return glob.glob(os.path.join(folder, '**', '*' + extension),
                         recursive = include_subfolders)

    def create_folder(self, folder, subfolder = None):
        """Creates folder path."""
        if subfolder:
            if folder and os.path.isdir(folder):
                folder = os.path.join(folder, subfolder)
            else:
                folder = os.path.join(getattr(self, folder), subfolder)
        self._make_folder(folder = folder)
        return folder

    def create_path(self, folder = None, file_name = None, file_format = None,
                    io_status = None):
        """Creates file path."""
        folder = self._check_folder(folder = folder,
                                    io_status = io_status)
        file_name = self._check_file_name(file_name = file_name,
                                          io_status = io_status)
        file_format = self._check_file_format(file_format = file_format,
                                              io_status = io_status)
        extension = self.extensions[file_format]
        if file_name == 'glob':
            file_path = self.create_batch(folder = folder,
                                          file_format = file_format)
        else:
            file_path = os.path.join(folder, file_name) + extension
        return file_path

    def initialize_writer(self, file_path, columns, encoding = None,
                          dialect = 'excel'):
        """Initializes writer object for line-by-line exporting to a .csv file.

        Parameters:
            file_path: a complete path to the file being created and written
                to.
            columns: a list of column names to be added to the first row of the
                file as column headers.
            encoding: a python encoding type. If none is provided, the default
                option is used.
            dialect: the specific type of csv file created.
        """
        if not columns:
            error = 'initialize_writer requires columns as a list type'
            raise TypeError(error)
        encoding = self._check_encoding()
        with open(file_path, mode = 'w', newline = '',
                  encoding = encoding) as self.output_series:
            self.writer = csv.writer(self.output_series, dialect = dialect)
            self.writer.writerow(columns)
        return self

    def inject(self, instance, sections, override = True):
        """Stores the default paths in the passed instance.

        Parameters:

            instance: either a class instance or class to which attributes
                should be added.
            sections: list of paths to be added to passed class. Data import
                and export paths are automatically added.
            override: if True, even existing attributes in instance will be
                replaced by items from this class.
        """
        instance.data_in = self.path_in
        instance.data_out = self.path_out
        for section in self.listify(sections):
            if hasattr(self, section + '_in') and override:
                setattr(instance, section + '_in',
                        getattr(self, section + '_in'))
                setattr(instance, section + '_out',
                        getattr(self, section + '_out'))
            elif override:
                setattr(instance, section, getattr(self, section))
        return

    def iterate(self, plans, ingredients = None, return_ingredients = True):
        """Iterates through a list of files contained in self.batch and
        applies the plans created by a Planner method (or subclass).

        Parameters:
            plans: an attribute of a Planner method (or subclass) containing
                methods used to modify an Ingredients instance.
            ingredients: an instance of Ingredients (or subclass).
            return_ingredients: a boolean value indicating whether ingredients
                should be returned by this method.
        """
        if ingredients:
            for file_path in self.batch:
                ingredients.source = self.load(file_path = file_path)
                for plan in plans:
                    ingredients = plan.perform(ingredients = ingredients)
            if return_ingredients:
                return ingredients
            else:
                return self
        else:
            for file_path in self.batch:
                for plan in plans:
                    plan.perform()
            return self

    def load(self, file_path = None, folder = None, file_name = None,
             file_format = None, **kwargs):
        """Imports file by calling appropriate method based on file_format. If
        the various arguments are not passed, default values are used. If
        file_path is passed, folder and file_name are ignored.

        Parameters:
            file_path: a complete file path for the file to be loaded.
            folder: a path to the folder from where the file should be loaded
                (not used if file_path is passed).
            file_name: a string containing the name of the file to be loaded
                without the file extension (not used if file_path is passed).
            file_format: a string matching one the file formats in
                self.extensions.
            kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.
        """
        file_format = self._check_file_format(file_format = file_format,
                                              io_status = 'import')
        if not file_path:
            file_path = self.create_path(folder = folder,
                                         file_name = file_name,
                                         file_format = file_format,
                                         io_status = 'import')
        if isinstance(file_path, str):
            return getattr(self, '_load_' + file_format)(file_path = file_path,
                                                         **kwargs)
        elif isinstance(file_path, list):
            error = 'file_path is a glob list - use iterate instead'
            raise TypeError(error)
        else:
            return file_path

    def prepare(self):
        """Creates data and results folders as well as other default subfolders
        (mirroring the cookie_cutter folder tree by default).
        """
        self._check_root_folder()
        self.add_folders(root_folder = self.root,
                         subfolders = [self.data_folder, self.results_folder])
        self.add_folders(root_folder = self.data,
                         subfolders = self.data_subfolders)
        return self

    def save(self, variable, file_path = None, folder = None, file_name = None,
             file_format = None, **kwargs):
        """Exports file by calling appropriate method based on file_format. If
        the various arguments are not passed, default values are used. If
        file_path is passed, folder and file_name are ignored.

        Parameters:
            variable: the variable being exported.
            file_path: a complete file path for the file to be saved.
            folder: a path to the folder where the file should be saved (not
                used if file_path is passed).
            file_name: a string containing the name of the file to be saved
                without the file extension (not used if file_path is passed).
            file_format: a string matching one the file formats in
                self.extensions.
            kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.
        """
        # Changes boolean values to 1/0 if self.boolean_out = False
        variable = self._check_boolean_out(variable = variable)
        file_format = self._check_file_format(file_format = file_format,
                                              io_status = 'export')
        if not file_path:
            file_path = self.create_path(folder = folder,
                                         file_name = file_name,
                                         file_format = file_format,
                                         io_status = 'export')
        getattr(self, '_save_' + file_format)(variable, file_path, **kwargs)
        return

    def perform(self):
        """Injects Inventory instance into base SimpleClass."""
        self._inject_base()
        return self




@dataclass
class Ingredients(SimpleClass):
    """Imports, stores, and exports pandas DataFrames and Series, as well as
    related information about those data containers.

    Ingredients uses pandas DataFrames or Series for all data storage, but it
    utilizes faster numpy methods where possible to increase performance.
    Ingredients stores the data itself as well as related variables containing
    information about the data.

    DataFrames stored in ingredients can be imported and exported using the
    load and save methods from the Inventory class.

    Ingredients adds easy-to-use methods for common feature engineering
    techniques. In addition, any user function can be applied to a DataFrame
    or Series contained in Ingredients by using the apply method.

    Parameters:

        df: a pandas DataFrame, Series, or a file_path. This argument should be
            passed if the user has a pre-existing dataset.
        default_df: a string listing the current default DataFrame or Series
            attribute that will be used when a specific DataFrame is not passed
            to a method within the class. The default value is initially set to
            'df'. The decorator check_df will look to the default_df to pick
            the appropriate DataFrame in situatios where no DataFrame is passed
            to a method.
        x, y, x_train, y_train, x_test, y_test, x_val, y_val: DataFrames or
            Series, or file paths. These  need not be passed when the class is
            instanced. They are merely listed for users who already have divided
            datasets and still wish to use the siMpLify package.
        datatypes: dictionary containing column names and datatypes for
            DataFrames or Series. Ingredients assumes that all data containers
            within the instance are related and share a pool of column names and
            types.
        prefixes: dictionary containing list of prefixes for columns and
            corresponding datatypes for default DataFrame. Ingredients assumes
            that all data containers within the instance are related and share a
            pool of column names and types.
        auto_prepare: a boolean variable indicating whether prepare method
            should be called when the class is instanced. This should
            generally be set to True.
        auto_perform: a boolean variable indicating whether the 'perform' method
            should be called when the class is instanced. This should only be
            set to True if the any of the DataFrame attributes is a file
            path and you want the file loaded into that attribute.

    """
    df : object = None
    default_df : str = 'df'
    x : object = None
    y : object = None
    x_train : object = None
    y_train : object = None
    x_test : object = None
    y_test : object = None
    x_val : object = None
    y_val : object = None
    datatypes : object = None
    prefixes : object = None
    auto_prepare : bool = True
    auto_perform : bool = False

    def __post_init__(self):
        super().__post_init__()
        return self

    """ Magic Methods """

    def __getattr__(self, attr):
        """Returns values from column datatypes, column datatype dictionary,
        and section prefixes dictionary.

        Parameters:
            attr: attribute sought.
        """
        if attr in ['x', 'y', 'x_train', 'y_train', 'x_test', 'y_test']:
            return self.__dict__[self.options[attr]]
        elif attr in ['booleans', 'floats', 'integers', 'strings',
                      'categoricals', 'lists', 'datetimes', 'timedeltas']:
            return self._get_columns_by_type(attr[:-1])
        elif attr in ['numerics']:
            return (self._get_columns_by_type('float')
                    + self._get_columns_by_type('integer'))
        elif (attr in ['scalers', 'encoders', 'mixers']
              and attr not in self.__dict__):
            return getattr(self, '_get_default_' + attr)()
        # elif attr in ['columns']:
        #     if not self.datatypes:
        #         self.datatypes = {}
        #     return self.datatypes
        # elif attr in ['sections']:
        #     if not self.prefixes:
        #         self.prefixes = {}
            # return self.prefixes
        elif attr in self.__dict__:
            return self.__dict__[attr]
        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError
        else:
            return None

    def __setattr__(self, attr, value):
        """Sets values in column datatypes, column datatype dictionary, and
        section prefixes dictionary.

        Parameters:
            attr: string of attribute name to be set.
            value: value of the set attribute.
        """
        if attr in ['booleans', 'floats', 'integers', 'strings',
                    'categoricals', 'lists', 'datetimes', 'timedeltas']:
            self.__dict__['datatypes'].update(
                    dict.fromkeys(self.listify(
                            self._all_datatypes[attr[:-1]]), value))
            return self
        # elif attr in ['columns']:
        #     self.__dict__['datatypes'].update({attr: value})
        #     return self
        # elif attr in ['sections']:
        #     if not self.prefixes:
        #         self.__dict__['prefixes'] = {attr : value}
        #     else:
        #         self.__dict__['prefixes'].update({attr : value})
            # return self
        else:
            self.__dict__[attr] = value
            return self

    """ Decorators """

    def check_df(method):
        """Decorator which automatically uses the default DataFrame if one
        is not passed to the decorated method.

        Parameters:
            method: wrapped method.
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            argspec = getfullargspec(method)
            unpassed_args = argspec.args[len(args):]
            if 'df' in argspec.args and 'df' in unpassed_args:
                kwargs.update({'df' : getattr(self, self.default_df)})
            return method(self, *args, **kwargs)
        return wrapper

    def column_list(method):
        """Decorator which creates a complete column list from kwargs passed
        to wrapped method.

        Parameters:
            method: wrapped method.
        """
        arguments_to_check = ['columns', 'prefixes', 'mask']
        new_kwargs = {}
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            argspec = getfullargspec(method)
            unpassed_args = argspec.args[len(args):]
            if ('columns' in unpassed_args
                    and 'prefixes' in unpassed_args
                    and 'mask' in unpassed_args):
                columns = list(self.datatypes.keys())
            else:
                for argument in arguments_to_check:
                    if argument in kwargs:
                        new_kwargs[argument] = kwargs[argument]
                    else:
                        new_kwargs[argument] = None
                    if argument in ['prefixes', 'mask'] and argument in kwargs:
                        del kwargs[argument]
                columns = self.create_column_list(**new_kwargs)
                kwargs.update({'columns' : columns})
            return method(self, **kwargs)
        return wrapper

    """ Properties """

    @property
    def full(self):
        """Returns the full dataset divided into x and y twice."""
        return (self.options['x'], self.options['y'],
                self.options['x'], self.options['y'])

    @property
    def test(self):
        """Returns the test data."""
        return self.options['x_test'], self.options['y_test']

    @property
    def train(self):
        """Returns the training data."""
        return self.options['x_train'], self.options['y_train']

    @property
    def train_test(self):
        """Returns the training and testing data."""
        return (*self.train, *self.test)

    @property
    def train_test_val(self):
        """Returns the training, test, and validation data."""
        return (*self.train, *self.test, *self.val)

    @property
    def train_val(self):
        """Returns the training and validation data."""
        return (*self.train, *self.val)

    @property
    def val(self):
        """Returns the validation data."""
        return self.options['x_val'], self.options['y_val']

    @property
    def xy(self):
        """Returns the full dataset divided into x and y."""
        return self.options['x'], self.options['y']

    """ private methods """

    def _check_columns(self, columns = None):
        """Returns self.datatypes if columns doesn't exist.

        Parameters:
            columns: list of column names."""
        return columns or list(self.datatypes.keys())

    @check_df
    def _crosscheck_columns(self, df = None):
        """Removes any columns in datatypes dictionary, but not in df."""
        for column in self.datatypes.keys():
            if column not in df.columns:
                del self.datatypes[column]
        return self

    def plan(self):
        """Sets defaults for Ingredients when class is instanced."""
        # Declares dictionary of DataFrames contained in Ingredients to allow
        # temporary remapping of attributes in __getattr__. __setattr does
        # not use this mapping.
        self.options = {'x' : 'x',
                        'y' : 'y',
                        'x_train' : 'x_train',
                        'y_train' : 'y_train',
                        'x_test' : 'x_test',
                        'y_test' : 'y_test',
                        'x_val' : 'x_val',
                        'y_val' : 'y_val'}
        # Copies 'options' so that original mapping is preserved.
        self.default_options = self.options.copy()
        self.all_datatypes = DataTypes()
        if not self.datatypes:
            self.datatypes = {}
        if not self.prefixes:
            self.prefixes = {}
        # Maps class properties to appropriate DataFrames using the default
        # train_test setting.
        self._remap_dataframes(data_to_use = 'train_test')
        # Initializes a list of dropped column names so that users can track
        # which features are omitted from analysis.
        self.dropped_columns = []
        return self

    def _get_columns_by_type(self, datatype):
        """Returns list of columns of the specified datatype.

        Parameters:
            datatype: string matching datatype in 'all_datatypes'.
        """
        return [k for k, v in self.datatypes.items() if v == datatype]

    def _get_default_encoders(self):
        return self.categoricals

    def _get_default_mixers(self):
        return []

    def _get_default_scalers(self):
        return self.integers + self.floats

    def _initialize_datatypes(self, df = None):
        """Initializes datatypes for columns of pandas DataFrame or Series if
        not already provided.
        """
        check_order = [df, getattr(self, self.default_df), self.x,
                       self.x_train]
        for _data in check_order:
            if isinstance(_data, pd.DataFrame) or isinstance(_data, pd.Series):
                if not self.datatypes:
                    self.infer_datatypes(df = _data)
                else:
                    self._crosscheck_columns(df = _data)
                break
        return self

    def _remap_dataframes(self, data_to_use = None):
        """Remaps DataFrames returned by various properties of Ingredients so
        that methods and classes of siMpLify can use the same labels for
        analyzing the Ingredients DataFrames.

        Parameters:
            data_to_use: a string corresponding to a class property indicating
                which set of data is to be returned when the corresponding
                property is called.
        """
        if not data_to_use:
            data_to_use = 'train_test'
        # Sets values in self.options which contains the mapping for class
        # attributes and DataFrames as determined in __getattr__.
        if data_to_use == 'train_test':
            self.options = self.default_options.copy()
        elif data_to_use == 'train_val':
            self.options['x_test'] = 'x_val'
            self.options['y_test'] = 'y_val'
        elif data_to_use == 'full':
            self.options['x_train'] = 'x'
            self.options['y_train'] = 'y'
            self.options['x_test'] = 'x'
            self.options['y_test'] = 'y'
        elif data_to_use == 'train':
            self.options['x'] = 'x_train'
            self.options['y'] = 'y_train'
        elif data_to_use == 'test':
            self.options['x'] = 'x_test'
            self.options['y'] = 'y_test'
        elif data_to_use == 'val':
            self.options['x'] = 'x_val'
            self.options['y'] = 'y_val'
        return self

    """ Public Methods """

    @check_df
    def add_unique_index(self, df = None, column = 'index_universal',
                         make_index = False):
        """Creates a unique integer index for each row.

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            column: string containing the column name for the index.
            make_index: boolean value indicating whether the index column
                should be made the index of the DataFrame."""
        if isinstance(df, pd.DataFrame):
            df[column] = range(1, len(df.index) + 1)
            self.datatypes.update({column, int})
            if make_index:
                df.set_index(column, inplace = True)
        else:
            error = 'To add an index, df must be a pandas DataFrame.'
            TypeError(error)
        return self

    @check_df
    def apply(self, df = None, func = None, **kwargs):
        """Allows users to pass a function to Ingredients instance which will
        be applied to the passed DataFrame (or uses default_df if none is
        passed).

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            func: function to be applied to the DataFrame.
            **kwargs: any arguments to be passed to func.
        """
        df = func(df, **kwargs)
        return self

    @column_list
    @check_df
    def auto_categorize(self, df = None, columns = None, threshold = 10):
        """Automatically assesses each column to determine if it has less than
        threshold unique values and is not boolean. If so, that column is
        converted to category type.

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            columns: a list of column names.
            threshold: integer of unique values necessary to form a category.
                If there are less unique values than the threshold, the column
                is converted to a category type. Otherwise, it will remain its
                current datatype.
        """
        for column in self._check_columns(columns):
            if column in df.columns:
                if not column in self.booleans:
                    if df[column].nunique() < threshold:
                        df[column] = df[column].astype('category')
                        self.datatypes[column] = 'categorical'
            else:
                error = column + ' is not in ingredients DataFrame'
                raise KeyError(error)
        return self

    @column_list
    @check_df
    def change_datatype(self, df = None, columns = None, datatype = str):
        """Changes column datatypes of columns passed or columns with the
        prefixes passed. datatype becomes the new datatype for the columns.

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            columns: a list of column names.
            prefixes: a list of prefix names.
            datatype: a string containing the datatype to convert the columns
                and columns with prefixes to.
        """
        for column in columns:
            self.datatypes[column] = datatype
        self.convert_column_datatypes(df = df)
        return self

    @check_df
    def conform(self, df = None, step = None):
        """Adjusts some of the siMpLify-specific datatypes to the appropriate
        datatype based upon the current step.

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            step: string corresponding to the current state.
        """
        self.step = step
        for column, datatype in self.datatypes.items():
            if self.step in ['reap', 'clean']:
                if datatype in ['category', 'encoder', 'interactor']:
                    self.datatypes[column] = str
            elif self.step in ['bundle', 'deliver']:
                if datatype in ['list', 'pattern']:
                    self.datatypes[column] = 'category'
        self.convert_column_datatypes(df = df)
        return self

    @check_df
    def convert_column_datatypes(self, df = None, raise_errors = False):
        """Attempts to convert all column data to the datatypes in
        'datatypes' dictionary.

        Parameters:
            df: pandas DataFrame or Series. If none is provided, the default
                DataFrame or Series is used.
            raise_errors: a boolean variable indicating whether errors should
                be raised when converting datatypes or ignored.
        """
        if raise_errors:
            raise_errors = 'raise'
        else:
            raise_errors = 'ignore'
        for column, datatype in self.datatypes.items():
            if not isinstance(datatype, str):
                df[column].astype(dtype = datatype,
                                  copy = False,
                                  errors = raise_errors)
        # Attempts to downcast datatypes to simpler forms if possible.
        self.downcast(df = df)
        return self

    @column_list
    @check_df
    def convert_rare(self, df = None, columns = None, threshold = 0):
        """Converts categories rarely appearing within categorical columns
        to empty string if they appear below the passed threshold. threshold is
        defined as the percentage of total rows.

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            columns: a list of columns to check. If not passed, all columns
                in 'datatypes' listed as 'categorical' type are used.
            threshold: a float indicating the percentage of values in rows
                below which a default value is substituted.
        """
        if not columns:
            columns = self.categoricals
        for column in columns:
            if column in df.columns:
                df['value_freq'] = (
                        df[column].value_counts() / len(df[column]))
                df[column] = np.where(df['value_freq'] <= threshold,
                                      self.default_values['categorical'],
                                      df[column])
            else:
                error = column + ' is not in DataFrame'
                raise KeyError(error)
        if 'value_freq' in df.columns:
            df.drop('value_freq', axis = 'columns', inplace = True)
        return self

    @check_df
    def create_column_list(self, df = None, columns = None, prefixes = None,
                           mask = None):
        """Dynamically creates a new column list from a list of columns and/or
        lists of prefixes, or boolean mask.

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            columns: list of columns.
            prefixes: list of prefixes for columns.
            mask: numpy array, list, or pandas Series, of booleans of columns.
        """
        column_names = []
        if (isinstance(mask, np.ndarray)
                or isinstance(mask, list)
                or isinstance(mask, pd.Series)):
            for boolean, feature in zip(mask, list(df.columns)):
                if boolean:
                    column_names.append(feature)
        else:
            temp_list = []
            prefixes_list = []
            if prefixes:
                for prefix in self.listify(prefixes):
                    temp_list = [col for col in df if col.startswith(prefix)]
                    prefixes_list.extend(temp_list)
            if columns:
                if prefixes:
                    column_names = self.listify(columns) + prefixes_list
                else:
                    column_names = self.listify(columns)
            else:
                column_names = prefixes_list
        return column_names

    @column_list
    def create_series(self, columns = None, return_series = True):
        """Creates a Series (row) with the datatypes in columns.

        Parameters:
            columns: a list of index names for pandas series.
            return_series: boolean value indicating whether the Series should
                be returned (True) or assigned to attribute named in default_df
                (False):
        """
        # If columns is not passed, the keys of self.datatypes are used.
        if not columns and self.datatypes:
            columns = list(self.datatypes.keys())
        row = pd.Series(index = columns)
        # Fills series with default_values based on datatype.
        if self.datatypes:
            for column, datatype in self.datatypes.items():
                row[column] = self.default_values[datatype]
        if return_series:
            return row
        else:
            setattr(self, self.default_df, row)
            return self

    @column_list
    @check_df
    def decorrelate(self, df = None, columns = None, threshold = 0.95):
        """Drops all but one column from highly correlated groups of columns.
        threshold is based upon the .corr() method in pandas. columns can
        include any datatype accepted by .corr(). If columns is set to None,
        all columns in the DataFrame are tested.

        Parameters:
            df: a pandas DataFrame.
            threshold: a float indicating the level of correlation using
                pandas corr method above which a column is dropped.
        """
        if columns:
            corr_matrix = df[columns].corr().abs()
        else:
            corr_matrix = df.corr().abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape),
                                          k = 1).astype(np.bool))
        corrs = [col for col in upper.corrs if any(upper[col] > threshold)]
        self.drop_columns(columns = corrs)
        return self

    @column_list
    @check_df
    def downcast(self, df = None, columns = None):
        """Decreases memory usage by downcasting datatypes. For numerical
        datatypes, the method attempts to cast the data to unsigned integers if
        possible.

        Parameters:
            df: a pandas DataFrame.
            columns: a list of columns to downcast
        """
        for column in self._check_columns(columns):
            if column in df.columns:
                if self.datatypes[column] in ['boolean']:
                    df[column] = df[column].astype(bool)
                elif self.datatypes[column] in ['integer', 'float']:
                    try:
                        df[column] = pd.to_numeric(df[column],
                                                   downcast = 'integer')
                        if min(df[column] >= 0):
                            df[column] = pd.to_numeric(df[column],
                                                       downcast = 'unsigned')
                    except ValueError:
                        df[column] = pd.to_numeric(df[column],
                                                   downcast = 'float')
                elif self.datatypes[column] in ['categorical']:
                    df[column] = df[column].astype('category')
                elif self.datatypes[column] in ['list']:
                    df[column].apply(self.listify,
                                     axis = 'columns',
                                     inplace = True)
                elif self.datatypes[column] in ['datetime']:
                    df[column] = pd.to_datetime(df[column])
                elif self.datatypes[column] in ['timedelta']:
                    df[column] = pd.to_timedelta(df[column])
            else:
                error = column + ' is not in DataFrame'
                raise KeyError(error)
        return self

    @column_list
    @check_df
    def drop_columns(self, df = None, columns = None):
        """Drops list of columns and columns with prefixes listed. In addition,
        any dropped columns are stored in the cumulative dropped_columns
        list.

        Parameters:
            df: pandas DataFrame or Series. If none is provided, the default
                DataFrame or Series is used.
            columns: list of columns to drop.
            prefixes: list of prefixes for columns to drop.
            mask: numpy array, list, or pandas Series, of booleans of columns
                to drop.
        """
        if isinstance(df, pd.DataFrame):
            df.drop(columns, axis = 'columns', inplace = True)
        else:
            df.drop(columns, inplace = True)
        self.dropped_columns.extend(columns)
        return self

    @column_list
    @check_df
    def drop_infrequent(self, df = None, columns = None, threshold = 0):
        """Drops boolean columns that rarely are True. This differs
        from the sklearn VarianceThreshold class because it is only
        concerned with rare instances of True and not False. This enables
        users to set a different variance threshold for rarely appearing
        information. threshold is defined as the percentage of total rows (and
        not the typical variance formulas used in sklearn).

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            columns: a list of columns to check. If not passed, all boolean
                columns will be used.
            threshold: a float indicating the percentage of True values in a
                boolean column that must exist for the column to be kept.
        """
        if not columns:
            columns = self.booleans
        infrequents = []
        for column in self.booleans:
            if column in columns:
                if df[column].mean() < threshold:
                    infrequents.append(column)
        self.drop_columns(columns = infrequents)
        return self

    @check_df
    def infer_datatypes(self, df = None):
        """Infers column datatypes and adds those datatypes to types. This
        method is an alternative to default pandas methods which can use
        complex datatypes (e.g., int8, int16, int32, int64, etc.). This also
        allows the user to choose which datatypes to look for by changing the
        default_values dictionary. Non-standard python datatypes cannot be
        inferred.

        Parameters:
            df: pandas DataFrame or Series. If none is provided, the default
                DataFrame or Series is used.
        """
        if not self.datatypes:
            self.datatypes = {}
        for datatype in self.all_datatypes.values():
            type_columns = df.select_dtypes(
                include = [datatype]).columns.to_list()
            self.datatypes.update(
                dict.fromkeys(type_columns,
                              self.all_datatypes[datatype]))
        return self

    def prepare(self):
        """Prepares Ingredients class instance."""
        if self.verbose:
            print('Preparing ingredients')
        # If 'df' or other DataFrame attribute is a file path, the file located
        # there is imported.
        for df_name in self.options.keys():
            if (not(isinstance(getattr(self, df_name), pd.DataFrame) or
                    isinstance(getattr(self, df_name), pd.Series))
                    and getattr(self, df_name)
                    and os.path.isfile(getattr(self, df_name))):
                self.load(name = df_name, file_path = self.df)
        # If datatypes passed, checks to see if columns are in df. Otherwise,
        # datatypes are inferred.
        self._initialize_datatypes()
        return self

    def save_dropped(self, file_name = 'dropped_columns', file_format = 'csv'):
        """Saves dropped_columns into a file

        Parameters:
            file_name: string containing name of file to be exported.
            file_format: string of file extension from Inventory.extensions.
        """
        # Deduplicates dropped_columns list
        self.dropped_columns = self.deduplicate(self.dropped_columns)
        if self.dropped_columns:
            if self.verbose:
                print('Exporting dropped feature list')
            self.inventory.save(variable = self.dropped_columns,
                                folder = self.inventory.experiment,
                                file_name = file_name,
                                file_format = file_format)
        elif self.verbose:
            print('No features were dropped during preprocessing.')
        return

    @column_list
    @check_df
    def smart_fill(self, df = None, columns = None):
        """Fills na values in DataFrame to defaults based upon the datatype
        listed in the columns dictionary.

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            columns: list of columns to fill missing values in.
        """
        for column in self._check_columns(columns):
            if column in df:
                default_value = self.all_datatypes.default_values[
                        self.datatypes[column]]
                df[column].fillna(default_value, inplace = True)
            else:
                error = column + ' is not in DataFrame'
                raise KeyError(error)
        return self

    @check_df
    def split_xy(self, df = None, label = 'label'):
        """Splits df into x and y based upon the label passed.

        Parameters:
            df: a pandas DataFrame.
            label: name of column(s) to be stored in self.y
        """
        self.x = df.drop(label, axis = 'columns')
        self.y = df[label]
        # Drops columns in self.y from datatypes dictionary and stores its
        # datatype in 'label_datatype'.
        self.label_datatype = {label : self.datatypes[label]}
        del self.datatypes[label]
        return self

def convert_time(seconds):
    """Function that converts seconds into hours, minutes, and seconds."""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return hours, minutes, seconds

def timer(process = None):
    """Decorator for computing the length of time a process takes.

    Parameters:
        process: string containing name of class or method."""

    if not process:
        if isinstance(process, FunctionType):
            process = process.__name__
        else:
            process = process.__class__.__name__

    def shell_timer(_function):

        def decorated(*args, **kwargs):
            perform_time = time.time()
            result = _function(*args, **kwargs)
            total_time = time.time() - perform_time
            h, m, s = convert_time(total_time)
            print(f'{process} completed in %d:%02d:%02d' % (h, m, s))
            return result

        return decorated

    return shell_timer
