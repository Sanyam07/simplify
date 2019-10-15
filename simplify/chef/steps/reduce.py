"""
.. module:: reduce
:synopsis: drops features based upon algorithmic criteria
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

from simplify.core.technique import SimpleTechnique
from simplify.core.decorators import numpy_shield


"""DEFAULT_OPTIONS are declared at the top of a module with a SimpleClass
subclass because siMpLify uses a lazy importing system. This locates the
potential module importations in roughly the same place as normal module-level
import commands. A SimpleClass subclass will, by default, add the
DEFAULT_OPTIONS to the subclass as the 'options' attribute. If a user wants
to use another set of 'options' for a subclass, they just need to pass
'options' when the class is instanced.
"""
DEFAULT_OPTIONS = {
    'kbest': ['sklearn.feature_selection', 'SelectKBest'],
    'fdr': ['sklearn.feature_selection', 'SelectFdr'],
    'fpr': ['sklearn.feature_selection', 'SelectFpr'],
    'custom': ['sklearn.feature_selection', 'SelectFromModel'],
    'rank': ['simplify.critic.rank', 'RankSelect'],
    'rfe': ['sklearn.feature_selection', 'RFE'],
    'rfecv': ['sklearn.feature_selection', 'RFECV']}


@dataclass
class Reduce(SimpleTechnique):
    """Reduces features using different algorithms, including the model
    algorithm.

    Args:
        technique (str): name of technique.
        parameters (dict): dictionary of parameters to pass to selected
            algorithm.
        name (str): name of class for matching settings in the Idea instance
            and for labeling the columns in files exported by Critic.
        auto_publish (bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.
    """

    technique: object = None
    parameters: object = None
    name: str = 'reduce'
    auto_publish: bool = True

    def __post_init__(self):
        self.idea_sections = ['chef']
        super().__post_init__()
        return self

    def draft(self):
        super().draft()
#        self.scorers = {'f_classif': f_classif,
#                        'chi2': chi2,
#                        'mutual_class': mutual_info_classif,
#                        'mutual_regress': mutual_info_regression}
        self.selected_parameters = True
        return self

    # def _set_parameters(self, estimator):
#        if self.technique in ['rfe', 'rfecv']:
#            self.default_parameters = {'n_features_to_select': 10,
#                                       'step': 1}
#            self.runtime_parameters = {'estimator': estimator}
#        elif self.technique == 'kbest':
#            self.default_parameters = {'k': 10,
#                                       'score_func': f_classif}
#            self.runtime_parameters = {}
#        elif self.technique in ['fdr', 'fpr']:
#            self.default_parameters = {'alpha': 0.05,
#                                       'score_func': f_classif}
#            self.runtime_parameters = {}
#        elif self.technique == 'custom':
#            self.default_parameters = {'threshold': 'mean'}
#            self.runtime_parameters = {'estimator': estimator}
#        self._publish_parameters()
#        self._select_parameters()
#        self.parameters.update({'estimator': estimator})
#        if 'k' in self.parameters:
#            self.num_features = self.parameters['k']
#        else:
#            self.num_features = self.parameters['n_features_to_select']
        # return self

    def publish(self):
        super().publish()
        return self

    @numpy_shield
    def implement(self, ingredients, plan = None, estimator = None):
        if not estimator:
            estimator = plan.model.algorithm
        self._set_parameters(estimator)
        self.algorithm = self.options[self.technique](**self.parameters)
        if len(ingredients.x_train.columns) > self.num_features:
            self.algorithm.fit(ingredients.x_train, ingredients.y_train)
            mask = ~self.algorithm.get_support()
            ingredients.drop_columns(df = ingredients.x_train, mask = mask)
            ingredients.drop_columns(df = ingredients.x_test, mask = mask)
        return ingredients