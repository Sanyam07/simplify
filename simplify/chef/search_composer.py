"""
.. module:: search composer
:synopsis: creates siMpLify-compatible hyperparameter search objects
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

from scipy.stats import randint, uniform

from simplify.chef.chef_composer import (ChefAlgorithm, ChefComposer,
                                         ChefTechnique)
from simplify.core.decorators import numpy_shield


@dataclass
class SearchComposer(ChefComposer):
    """Searches for optimal model hyperparameters using specified technique.

    Args:

    Returns:
        [type]: [description]
    """
    name: str = 'search_composer'
    algorithm_class: object = SearchAlgorithm
    technique_class: object = SearchTechnique

    def __post_init__(self):
        self.idea_sections = ['chef']
        super().__post_init__()
        return self

    """ Private Methods """

    def _get_conditional(self, technique: ChefTechnique, parameters: dict):
        """[summary]

        Args:
            technique (namedtuple): [description]
            parameters (dict): [description]
        """
        if 'refit' in parameters and isinstance(parameters['scoring'], list):
            parameters['scoring'] = parameters['scoring'][0]
        return parameters

    """ Core siMpLify Methods """

    def draft(self):
        self.bayes = Technique(
            name = 'bayes',
            module = 'bayes_opt',
            algorithm = 'BayesianOptimization',
            runtimes = {
                'f': 'estimator',
                'pbounds': 'space',
                'random_state': 'seed'})
        self.grid = Technique(
            name = 'grid',
            module = 'sklearn.model_selection',
            algorithm = 'GridSearchCV',
            runtimes = {
                'estimator': 'estimator',
                'param_distributions': 'space',
                'random_state': 'seed'})
        self.random = Technique(
            name = 'random',
            module = 'sklearn.model_selection',
            algorithm = 'RandomizedSearchCV',
            runtimes = {
                'estimator': 'estimator',
                'param_distributions': 'space',
                'random_state': 'seed'})
        super().draft()
        return self


@dataclass
class SearchAlgorithm(SimpleAlgorithm):
    """[summary]

    Args:
        object ([type]): [description]
    """
    technique: str
    algorithm: object
    parameters: object
    data_dependents: object = None
    hyperparameter_search : bool = False
    space: object = None
    name: str = 'search'

    def __post_init__(self):
        super().__post_init__()
        return self

    @numpy_shield
    def publish(self, ingredients: Ingredients, data_to_use: str):
        """[summary]

        Args:
            ingredients ([type]): [description]
            data_to_use ([type]): [description]
        """
        if self.technique in ['random', 'grid']:
            return self.algorithm.fit(
                X = getattr(ingredients, ''.join(['x_', data_to_use])),
                Y = getattr(ingredients, ''.join(['y_', data_to_use])),
                **kwargs)