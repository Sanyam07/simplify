
"""
.. module:: technique
:synopsis: catalog of algorithms for selection and implementation
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from simplify.core.base import SimpleClass
from simplify.core.decorators import numpy_shield
from simplify.core.parameters import SimpleParameters


@dataclass
class SimpleTechnique(SimpleClass):
    """Parent class for various techniques in the siMpLify package.

    SimpleTechnique is the lowest-level parent class in the siMpLify package.
    It follows the general structure of SimpleClass, but is focused on storing
    and applying single techniques to data or other variables. It is included,
    in part, to achieve the highest level of compatibility with scikit-learn as
    currently possible.

    Not every low-level technique needs to a subclass of SimpleTechnique. For
    example, many of the algorithms used in the Cookbook steps (RandomForest,
    XGBClassifier, etc.) are dependencies that are fully integrated into the
    siMpLify architecture without wrapping them into a SimpleTechnique
    subclass. SimpleTechnique is used for custom techniques and for
    dependencies that require a substantial adapter to integrate into siMpLify.

    Args:
        technique(str): name of technique that matches key in 'options'.
        parameters(dict): parameters to be attached to algorithm in 'options'
            corresponding to 'technique'. This parameter need not be passed to
            the SimpleTechnique subclass if the parameters are in the Idea
            instance or if the user wishes to use default parameters.
        name(str): designates the name of the class which should be identical
            to the section of the Idea instance with relevant settings.
        auto_publish(bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.

    It is also a child class of SimpleClass. So, its documentation applies as
    well.

    """
    technique: object = None
    parameters: object = None
    name: str = 'generic_technique'
    auto_publish: bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    """ Private Methods """

    def _set_algorithm(self):
        """Creates 'algorithm' attribute and adds parameters."""
        if (self.exists('simplify_options')
                and self.technique in self.simplify_options):
            self.algorithm = self.options[self.technique](
                    technique = self.technique,
                    parameters = self.parameters)
        else:
            self.algorithm = self.options[self.technique](**self.parameters)
        return self

    def _set_parameters(self):
        """Creates final parameters for this instance's 'algorithm'."""
        self.parameters_factory = SimpleParameters()
        self.parameters = self.parameters_factory.implement(instance = self)
        if hasattr(self, '_parse_parameters'):
            self._parse_parameters()
        return self

    """ Core siMpLify Public Methods """

    def draft(self):
        """ Declares defaults for class."""
        super().draft()
        return self

    def publish(self):
        """Finalizes settings and creates an instance of the 'algorithm'."""
        if self.technique != 'none':
            super().publish()
            if hasattr(self, '_set_estimator'):
                self._set_estimator()
                self._set_parameters()
            else:
                self._set_parameters()
                self._set_algorithm()
        else:
            self.algorithm = None
        return self

    @numpy_shield
    def implement(self, ingredients, *args, **kwargs):
        """Generic implementation method for SimpleTechnique subclass.

        Args:
            ingredients(Ingredients): an instance of Ingredients or subclass.

        """
        if self.algorithm:
            if self.technique in self.simplify_options:
                ingredients = self.algorithm.implement(
                    ingredients, *args, **kwargs)
            else:
                self.algorithm.fit(
                    X = getattr(ingredients, 'x_' + self.data_to_train),
                    Y = getattr(ingredients, 'y_' + self.data_to_train),
                    *args, **kwargs)
                setattr(ingredients, 'x_' + self.data_to_train,
                        self.algorithm.transform(X = getattr(
                            ingredients, 'x_' + self.data_to_train)))
        return ingredients

    """ Scikit-Learn Compatibility Methods """

    def fit(self, x = None, y = None, ingredients = None):
        """Generic fit method for partial compatibility to sklearn.

        Args:
            x(DataFrame or ndarray): independent variables/features.
            y(DataFrame, Series, or ndarray): dependent variable(s)/feature(s)
            ingredients(Ingredients): instance of Ingredients containing
                x_train and y_train attributes (based upon possible remapping).

        Raises:
            AttributeError if no 'fit' method exists for local 'algorithm'.

        """
        if hasattr(self.algorithm, 'fit'):
            if isinstance(x, pd.DataFrame) or isinstance(x, np.ndarray):
                if y is None:
                    self.algorithm.fit(X = x)
                else:
                    self.algorithm.fit(X = x, Y = y)
            elif ingredients is not None:
                ingredients = self.algorithm.fit(
                    X = getattr(ingredients, 'x_' + self.data_to_train),
                    Y = getattr(ingredients, 'y_' + self.data_to_train))

        else:
            error = ('fit method does not exist for '
                     + self.technique + ' algorithm')
            raise AttributeError(error)
        return self

    def fit_transform(self, x = None, y = None, ingredients = None):
        """Generic fit_transform method for partial compatibility to sklearn

        Args:
            x(DataFrame or ndarray): independent variables/features.
            y(DataFrame, Series, or ndarray): dependent variable(s)/feature(s)
            ingredients(Ingredients): instance of Ingredients containing
                x_train and y_train attributes (based upon possible remapping).

        Returns:
            transformed x or ingredients, depending upon what is passed to the
                method.

        Raises:
            TypeError if DataFrame, ndarray, or ingredients is not passed to
                the method.

        """
        self.fit(x = x, y = y, ingredients = ingredients)
        if isinstance(x, pd.DataFrame) or isinstance(x, np.ndarray):
            return self.transform(x = x, y = y)
        elif ingredients is not None:
            return self.transform(ingredients = ingredients)
        else:
            error = 'fit_transform requires DataFrame, ndarray, or Ingredients'
            raise TypeError(error)

    def transform(self, x = None, y = None, ingredients = None):
        """Generic transform method for partial compatibility to sklearn.

        Args:
            x(DataFrame or ndarray): independent variables/features.
            y(DataFrame, Series, or ndarray): dependent variable(s)/feature(s)
            ingredients(Ingredients): instance of Ingredients containing
                x_train and y_train attributes (based upon possible remapping).

        Returns:
            transformed x or ingredients, depending upon what is passed to the
                method.

        Raises:
            AttributeError if no 'transform' method exists for local
                'algorithm'.

        """
        if hasattr(self.algorithm, 'transform'):
            if isinstance(x, pd.DataFrame) or isinstance(x, np.ndarray):
                if y is None:
                    return self.algorithm.transform(x)
                else:
                    return self.algorithm.transform(x, y)
            elif ingredients is not None:
                return self.algorithm.transform(
                    X = getattr(ingredients, 'x_' + self.data_to_train),
                    Y = getattr(ingredients, 'y_' + self.data_to_train))
        else:
            error = ('transform method does not exist for '
                     + self.technique + ' algorithm')
            raise AttributeError(error)
