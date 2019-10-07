"""
.. module:: model
:synopsis: Applies machine learning and statistical models to data
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

from scipy.stats import randint, uniform

from simplify.core.parameters import SimpleParameters
from simplify.core.technique import SimpleTechnique


@dataclass
class Model(SimpleTechnique):
    """Applies machine learning algorithms based upon user selections.

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
        self.idea_sections = ['chef']
        super().__post_init__()
        return self
    
    """ Private Methods """

    def _datatype_in_list(self, test_list, data_type):
        """Tests whether any item in a list is of the passed data type."""
        return any(isinstance(i, data_type) for i in test_list)

    def _get_conditional_parameters(self, parameters):
        if (self.technique in ['xgboost']
                and not 'scale_pos_weight' in parameters
                and hasattr(self, 'scale_pos_weight')):
            parameters.update(
                    {'scale_pos_weight': self.scale_pos_weight})
            if self.gpu:
                parameters.update({'tree_method': 'gpu_exact'})
        return parameters

    def _parse_parameters(self):
        """Parses parameters to determine if the user has created ranges of
        parameters. If so, parameters are divided between those to be searched
        and those that are fixed. If any parameters include a range of values,
        hyperparameter_search is set to True. Fixed parameters are stored in
        the parameters attribute. Ranges to be searched are stored in the
        space attribute.
        """
        self.hyperparameter_search = False
        self.space = {}
        new_parameters = {}
        for param, values in self.parameters.items():
            if isinstance(values, list):
                self.hyperparameter_search = True
                if self._datatype_in_list(values, float):
                    self.space.update({param: uniform(values[0], values[1])})
                elif self._datatype_in_list(values, int):
                    self.space.update({param: randint(values[0], values[1])})
            else:
                new_parameters.update({param: values})
        self.parameters = new_parameters
        return self   

    def _set_estimator(self):
        self.estimator = self.options[self.model_type](
            technique = self.technique)
        return self
        
    def _set_parameters(self):
        self.runtime_parameters = {'random_state': self.seed}
        self.parameters_factory = SimpleParameters()
        self.parameters = self.parameters_factory.implement(
            instance = self.estimator)
        self._parse_parameters()
        return self

    def _set_search(self):
        self.search = self.options['search'](
            technique = self.search_technique,
            parameters = self.idea['search_parameters'])
        self.search.space = self.space
        self.search.estimator = self.estimator.algorithm
        self.search.publish()
        return self    
        
    """ Core siMpLify Methods """

    def draft(self):
        super().draft()
        self.options = {
                'search': ['simplify.chef.steps.techniques.search', 'Search'],
                'classify': ['simplify.chef.steps.techniques.classify',
                             'Classify'],
                'cluster': ['simplify.chef.steps.techniques.cluster',
                            'Cluster'],
                'regress': ['simplify.chef.steps.techniques.regress',
                            'Regress']}
        self.checks.extend(['gpu'])
        return self

    def publish(self):
        if self.technique != 'none':
            self._set_estimator()
            self._set_parameters()
            if self.hyperparameter_search:
                self._set_search()             
        return self

    def implement(self, ingredients, plan = None):
        """Applies model from recipe to ingredients data."""
        if self.technique != 'none':
            if self.hyperparameter_search:
                self.algorithm = self.search.implement(
                    ingredients = ingredients)
            else:
                self.algorithm = self.estimator.implement(
                        ingredients = ingredients)
        return ingredients

    """ Scikit-Learn Compatibility Methods """

    def fit_transform(self, x, y = None):
        error = 'fit_transform is not implemented for machine learning models'
        raise NotImplementedError(error)

    def transform(self, x, y = None):
        error = 'transform is not implemented for machine learning models'
        raise NotImplementedError(error)  