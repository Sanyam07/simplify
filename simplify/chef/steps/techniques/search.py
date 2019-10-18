"""
.. module:: search
:synopsis: hyperparameter search algorithms
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass, field
from typing import Dict

from simplify.core.technique import ChefTechnique


"""DEFAULT_OPTIONS are declared at the top of a module with a SimpleClass
subclass because siMpLify uses a lazy importing system. This locates the
potential module importations in roughly the same place as normal module-level
import commands. A SimpleClass subclass will, by default, add the
DEFAULT_OPTIONS to the subclass as the 'options' attribute. If a user wants
to use another set of 'options' for a subclass, they just need to pass
'options' when the class is instanced.
"""
DEFAULT_OPTIONS = {
    'bayes': ['skopt', 'BayesSearchCV'],
    'grid': ['sklearn.model_selection', 'GridSearchCV'],
    'random': ['sklearn.model_selection', 'RandomizedSearchCV']}


@dataclass
class Search(ChefTechnique):
    """Searches for optimal model hyperparameters using specified technique.

    Args:
        technique (str): name of technique.
        parameters (dict): dictionary of parameters to pass to selected
            algorithm.
        name (str): name of class for matching settings in the Idea instance
            and for labeling the columns in files exported by Critic.
        auto_draft (bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to False for
            this class because of the complexity of adding a complete estimator
            before finalizing the search algorithm.
    """

    technique: object = None
    parameters: object = None
    name: str = 'search'
    auto_draft: bool = False
    options: Dict = field(default_factory = lambda: DEFAULT_OPTIONS)
    
    def __post_init__(self):
        self.idea_sections = ['chef']
        super().__post_init__()
        return self

    """ Private Methods """

    def _set_parameters(self):
        self.parameters.update(
            {'estimator': self.estimator.algorithm,
             'param_distributions': self.space,
             'random_state': self.seed})
        if 'refit' in self.parameters:
            self.parameters['scoring'] = self.listify(
                self.parameters['scoring'])[0]
        return self

    def _print_best_estimator(self):
        if self.verbose:
            print('Searching for best hyperparameters using',
                  self.technique, 'search algorithm')
            print('The', self.parameters['scoring'],
                  'score of the best estimator for the',
                  self.estimator.technique, ' model is',
                  f'{self.algorithm.best_score_: 4.4f}')
        return self

    """ Core siMpLify Methods """

    def draft(self):
        return self

    def implement(self, ingredients):
        self.algorithm.fit(ingredients.x_train, ingredients.y_train)
        self._print_best_estimator()
        self.best_estimator = self.algorithm.best_estimator_
        return self.best_estimator