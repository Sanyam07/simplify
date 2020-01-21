"""
.. module:: chef
:synopsis: machine learning made simple
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass
from dataclasses import field
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy.stats import randint, uniform

from simplify.core.book import Book
from simplify.core.repository import Repository
from simplify.core.repository import Sequence
from simplify.core.technique import TechniqueDefinition


@dataclass
class Cookbook(Book):
    """Standard class for iterable storage in the Chef subpackage.

    Args:
        name (Optional[str]): designates the name of the class used for internal
            referencing throughout siMpLify. If the class needs settings from
            the shared Idea instance, 'name' should match the appropriate
            section name in Idea. When subclassing, it is a good idea to use
            the same 'name' attribute as the base class for effective
            coordination between siMpLify classes. 'name' is used instead of
            __class__.__name__ to make such subclassing easier. Defaults to
            None. If not passed, __class__.__name__.lower() is used.
        iterable(Optional[str]): name of attribute for storing the main class
            instance iterable (called by __iter___). Defaults to 'chapters'.
        techiques (Optional['Repository']): a dictionary of options with
            'Technique' instances stored by step. Defaults to an empty
            'Repository' instance.
        chapters (Optional['Sequence']): iterable collection of steps and
            techniques to apply at each step. Defaults to an empty 'Sequence'
            instance.
        returns_data (Optional[bool]): whether the Scholar instance's 'apply'
            expects data when the Book instance is iterated. If False, nothing
            is returned. If true, 'data' is returned. Defaults to True.

    """
    name: Optional[str] = 'cookbook'
    iterable: Optional[str] = 'recipes'
    techniques: Optional['Repository'] = field(default_factory = Repository)
    chapters: Optional['Sequence'] = field(default_factory = Sequence)
    returns_data: Optional[bool] = True


    def _add_model_conditionals(self,
            technique: 'Technique',
            data: 'Ingredients') -> 'Technique':
        """Adds any conditional parameters to 'technique'

        Args:
            technique ('Technique'): an instance with 'algorithm' and
                'parameters' not yet combined.

        Returns:
            'Technique': with any applicable parameters added.

        """
        self._model_calculate_hyperparameters(
            technique = technique,
            ingredients = ingredients)
        if technique.technique in ['xgboost'] and self.gpu:
            technique.parameters['tree_method'] = 'gpu_exact'
        elif step in ['tensorflow']:
            technique.algorithm = make_tensorflow_model(
                technique = technique,
                ingredients = ingredients)
        return technique

    def _model_calculate_hyperparameters(self,
            technique: 'Technique',
            ingredients: 'Ingredients') -> 'Technique':
        """Computes hyperparameters from data.

        This method will include any heuristics or methods for creating smart
        algorithm parameters (without creating data leakage problems).

        This method currently only support xgboost's scale_pos_weight
        parameter. Future hyperparameter computations will be added as they
        are discovered.

        Args:
            technique ('Technique'): an instance with 'algorithm' and
                'parameters' not yet combined.

        Returns:
            'Technique': with any applicable parameters added.

        """
        if (technique.technique in ['xgboost']
                and self.calculate_hyperparameters):
            technique.parameters['scale_pos_weight'] = (
                    len(self.ingredients['y'].index) /
                    ((self.ingredients['y'] == 1).sum())) - 1
        return self

    """ Public Methods """

    def add_cleaves(self,
            cleave_group: str,
            prefixes: Union[List[str], str] = None,
            columns: Union[List[str], str] = None) -> None:
        """Adds cleaves to the list of cleaves.

        Args:
            cleave_group (str): names the set of features in the group.
            prefixes (Union[List[str], str]): name(s) of prefixes to columns to
                be included within the cleave.
            columns (Union[List[str], str]): name(s) of columns to be included
                within the cleave.

        """
        # if not self._exists('cleaves'):
        #     self.cleaves = []
        # columns = self.ingredients.make_column_list(
        #     prefixes = prefixes,
        #     columns = columns)
        # self.workers['cleaver'].add_techniques(
        #     cleave_group = cleave_group,
        #     columns = columns)
        # self.cleaves.append(cleave_group)
        return self


    # def _cleave(self, ingredients):
    #     if self.step != 'all':
    #         cleave = self.workers[self.step]
    #         drop_list = [i for i in self.test_columns if i not in cleave]
    #         for col in drop_list:
    #             if col in ingredients.x_train.columns:
    #                 ingredients.x_train.drop(col, axis = 'columns',
    #                                          inplace = True)
    #                 ingredients.x_test.drop(col, axis = 'columns',
    #                                         inplace = True)
    #     return ingredients

    # def _publish_cleaves(self):
    #     for group, columns in self.workers.items():
    #         self.test_columns.extend(columns)
    #     if self.parameters['include_all']:
    #         self.workers.update({'all': self.test_columns})
    #     return self

    # def add(self, cleave_group, columns):
    #     """For the cleavers in siMpLify, this step alows users to manually
    #     add a new cleave group to the cleaver dictionary.
    #     """
    #     self.workers.update({cleave_group: columns})
    #     return self


#        self.scorers = {'f_classif': f_classif,
#                        'chi2': chi2,
#                        'mutual_class': mutual_info_classif,
#                        'mutual_regress': mutual_info_regression}

    # # @numpy_shield
    # def publish(self, ingredients, plan = None, estimator = None):
    #     if not estimator:
    #         estimator = plan.model.algorithm
    #     self._set_parameters(estimator)
    #     self.algorithm = self.workers[self.step](**self.parameters)
    #     if len(ingredients.x_train.columns) > self.num_features:
    #         self.algorithm.fit(ingredients.x_train, ingredients.y_train)
    #         mask = ~self.algorithm.get_support()
    #         ingredients.drop_columns(df = ingredients.x_train, mask = mask)
    #         ingredients.drop_columns(df = ingredients.x_test, mask = mask)
    #     return ingredients

    # # @numpy_shield
    # def publish(self,
    #         ingredients: 'Ingredients',
    #         data_to_use: str,
    #         columns: list = None,
    #         **kwargs) -> 'Ingredients':
    #     """[summary]

    #     Args:
    #         ingredients (Ingredients): [description]
    #         data_to_use (str): [description]
    #         columns (list, optional): [description]. Defaults to None.
    #     """
    #     if self.step != 'none':
    #         if self.data_dependents:
    #             self._add_data_dependents(data = ingredients)
    #         if self.hyperparameter_search:
    #             self.algorithm = self._search_hyperparameters(
    #                 data = ingredients,
    #                 data_to_use = data_to_use)
    #         try:
    #             self.algorithm.fit(
    #                 X = getattr(ingredients, ''.join(['x_', data_to_use])),
    #                 Y = getattr(ingredients, ''.join(['y_', data_to_use])),
    #                 **kwargs)
    #             setattr(ingredients, ''.join(['x_', data_to_use]),
    #                     self.algorithm.transform(X = getattr(
    #                         ingredients, ''.join(['x_', data_to_use]))))
    #         except AttributeError:
    #             data = self.algorithm.publish(
    #                 data = ingredients,
    #                 data_to_use = data_to_use,
    #                 columns = columns,
    #                 **kwargs)
    #     return ingredients

    # def _set_parameters(self, estimator):
#        if self.step in ['rfe', 'rfecv']:
#            self.default = {'n_features_to_select': 10,
#                                       'step': 1}
#            self.runtime_parameters = {'estimator': estimator}
#        elif self.step == 'kbest':
#            self.default = {'k': 10,
#                                       'score_func': f_classif}
#            self.runtime_parameters = {}
#        elif self.step in ['fdr', 'fpr']:
#            self.default = {'alpha': 0.05,
#                                       'score_func': f_classif}
#            self.runtime_parameters = {}
#        elif self.step == 'custom':
#            self.default = {'threshold': 'mean'}
#            self.runtime_parameters = {'estimator': estimator}
#        self._publish_parameters()
#        self._select_parameters()
#        self.parameters.update({'estimator': estimator})
#        if 'k' in self.parameters:
#            self.num_features = self.parameters['k']
#        else:
#            self.num_features = self.parameters['n_features_to_select']
        # return self




# @dataclass
# class SearchComposer(ChefComposer):
#     """Searches for optimal model hyperparameters using specified step.

#     Args:

#     Returns:
#         [type]: [description]
#     """
#     name: str = 'search_composer'
#     algorithm_class: object = SearchTechniqueDefinition
#     step_class: object = SearchTechnique

#     def __post_init__(self) -> None:
#         self.idea_sections = ['chef']
#         super().__post_init__()
#         return self

#     """ Private Methods """

#     def _build_conditional(self, step: ChefTechnique, parameters: dict):
#         """[summary]

#         Args:
#             step (namedtuple): [description]
#             parameters (dict): [description]
#         """
#         if 'refit' in parameters and isinstance(parameters['scoring'], list):
#             parameters['scoring'] = parameters['scoring'][0]
#         return parameters
#         self.space = {}
#         if step.hyperparameter_search:
#             new_parameters = {}
#             for parameter, values in parameters.items():
#                 if isinstance(values, list):
#                     if self._datatype_in_list(values, float):
#                         self.space.update(
#                             {parameter: uniform(values[0], values[1])})
#                     elif self._datatype_in_list(values, int):
#                         self.space.update(
#                             {parameter: randint(values[0], values[1])})
#                 else:
#                     new_parameters.update({parameter: values})
#             parameters = new_parameters
#         return parameters

#     def _search_hyperparameter(self, ingredients: Ingredients,
#                                data_to_use: str):
#         search = SearchComposer()
#         search.space = self.space
#         search.estimator = self.algorithm
#         return search.publish(data = ingredients)

#     """ Core siMpLify Methods """

#     def draft(self) -> None:
#         self.bayes = Technique(
#             name = 'bayes',
#             module = 'bayes_opt',
#             algorithm = 'BayesianOptimization',
#             runtime = {
#                 'f': 'estimator',
#                 'pbounds': 'space',
#                 'random_state': 'seed'})
#         self.grid = Technique(
#             name = 'grid',
#             module = 'sklearn.model_selection',
#             algorithm = 'GridSearchCV',
#             runtime = {
#                 'estimator': 'estimator',
#                 'param_distributions': 'space',
#                 'random_state': 'seed'})
#         self.random = Technique(
#             name = 'random',
#             module = 'sklearn.model_selection',
#             algorithm = 'RandomizedSearchCV',
#             runtime = {
#                 'estimator': 'estimator',
#                 'param_distributions': 'space',
#                 'random_state': 'seed'})
#         super().draft()
#         return self


# @dataclass
# class SearchTechniqueDefinition(TechniqueDefinition):
#     """[summary]

#     Args:
#         object ([type]): [description]
#     """
#     step: str
#     algorithm: object
#     parameters: object
#     data_dependents: object = None
#     hyperparameter_search: bool = False
#     space: object = None
#     name: str = 'search'

#     def __post_init__(self) -> None:
#         super().__post_init__()
#         return self

#     @numpy_shield
#     def publish(self, ingredients: Ingredients, data_to_use: str):
#         """[summary]

#         Args:
#             ingredients ([type]): [description]
#             data_to_use ([type]): [description]
#         """
#         if self.step in ['random', 'grid']:
#             return self.algorithm.fit(
#                 X = getattr(ingredients, ''.join(['x_', data_to_use])),
#                 Y = getattr(ingredients, ''.join(['y_', data_to_use])),
#                 **kwargs)


@dataclass
class Cookware(Repository):
    """A dictonary of TechniqueDefinition options for the Chef subpackage.

    Args:
        contents (Optional[str, Any]): default stored dictionary. Defaults to
            an empty dictionary.
        wildcards (Optional[List[str]]): a list of corresponding properties
            which access sets of dictionary keys. If none is passed, the two
            included properties ('default' and 'all') are used.
        defaults (Optional[List[str]]): a list of keys in 'contents' which
            will be used to return items when 'default' is sought. If not
            passed, 'default' will be set to all keys.
        null_value (Optional[Any]): value to return when 'none' is accessed or
            an item isn't found in 'contents'. Defaults to None.

    """
    contents: Optional[Dict[str, Any]] = field(default_factory = dict)
    wildcards: Optional[List[str]] = field(default_factory = list)
    defaults: Optional[List[str]] = field(default_factory = list)
    null_value: Optional[Any] = None
    project: 'Project' = None

    def __post_init__(self) -> None:
        """Initializes 'defaults' and 'wildcards'."""
        super().__post_init__()
        if not self.contents:
            self._create_dictionary()
        return self

    def _create_dictionary(self) -> None:
        self.contents = {
            'filler': {
                'defaults': TechniqueDefinition(
                    name = 'defaults',
                    module = 'simplify.chef.algorithms',
                    algorithm = 'smart_fill',
                    default = {'defaults': {
                        'boolean': False,
                        'float': 0.0,
                        'integer': 0,
                        'string': '',
                        'categorical': '',
                        'list': [],
                        'datetime': 1/1/1900,
                        'timedelta': 0}}),
                'impute': TechniqueDefinition(
                    name = 'defaults',
                    module = 'sklearn.impute',
                    algorithm = 'SimpleImputer',
                    default = {'defaults': {}}),
                'knn_impute': TechniqueDefinition(
                    name = 'defaults',
                    module = 'sklearn.impute',
                    algorithm = 'KNNImputer',
                    default = {'defaults': {}})},
            'categorizer': {
                'automatic': TechniqueDefinition(
                    name = 'automatic',
                    module = 'simplify.chef.algorithms',
                    algorithm = 'auto_categorize',
                    default = {'threshold': 10}),
                'binary': TechniqueDefinition(
                    name = 'binary',
                    module = 'sklearn.preprocessing',
                    algorithm = 'Binarizer',
                    default = {'threshold': 0.5}),
                'bins': TechniqueDefinition(
                    name = 'bins',
                    module = 'sklearn.preprocessing',
                    algorithm = 'KBinsDiscretizer',
                    default = {
                        'strategy': 'uniform',
                        'n_bins': 5},
                    selected = True,
                    required = {'encode': 'onehot'})},
            'scaler': {
                'gauss': TechniqueDefinition(
                    name = 'gauss',
                    module = None,
                    algorithm = 'Gaussify',
                    default = {'standardize': False, 'copy': False},
                    selected = True,
                    required = {'rescaler': 'standard'}),
                'maxabs': TechniqueDefinition(
                    name = 'maxabs',
                    module = 'sklearn.preprocessing',
                    algorithm = 'MaxAbsScaler',
                    default = {'copy': False},
                    selected = True),
                'minmax': TechniqueDefinition(
                    name = 'minmax',
                    module = 'sklearn.preprocessing',
                    algorithm = 'MinMaxScaler',
                    default = {'copy': False},
                    selected = True),
                'normalize': TechniqueDefinition(
                    name = 'normalize',
                    module = 'sklearn.preprocessing',
                    algorithm = 'Normalizer',
                    default = {'copy': False},
                    selected = True),
                'quantile': TechniqueDefinition(
                    name = 'quantile',
                    module = 'sklearn.preprocessing',
                    algorithm = 'QuantileTransformer',
                    default = {'copy': False},
                    selected = True),
                'robust': TechniqueDefinition(
                    name = 'robust',
                    module = 'sklearn.preprocessing',
                    algorithm = 'RobustScaler',
                    default = {'copy': False},
                    selected = True),
                'standard': TechniqueDefinition(
                    name = 'standard',
                    module = 'sklearn.preprocessing',
                    algorithm = 'StandardScaler',
                    default = {'copy': False},
                    selected = True)},
            'splitter': {
                'group_kfold': TechniqueDefinition(
                    name = 'group_kfold',
                    module = 'sklearn.model_selection',
                    algorithm = 'GroupKFold',
                    default = {'n_splits': 5},
                    runtime = {'random_state': 'seed'},
                    selected = True),
                'kfold': TechniqueDefinition(
                    name = 'kfold',
                    module = 'sklearn.model_selection',
                    algorithm = 'KFold',
                    default = {'n_splits': 5, 'shuffle': False},
                    runtime = {'random_state': 'seed'},
                    selected = True,
                    required = {'shuffle': True}),
                'stratified': TechniqueDefinition(
                    name = 'stratified',
                    module = 'sklearn.model_selection',
                    algorithm = 'StratifiedKFold',
                    default = {'n_splits': 5, 'shuffle': False},
                    runtime = {'random_state': 'seed'},
                    selected = True,
                    required = {'shuffle': True}),
                'time': TechniqueDefinition(
                    name = 'time',
                    module = 'sklearn.model_selection',
                    algorithm = 'TimeSeriesSplit',
                    default = {'n_splits': 5},
                    runtime = {'random_state': 'seed'},
                    selected = True),
                'train_test': TechniqueDefinition(
                    name = 'train_test',
                    module = 'sklearn.model_selection',
                    algorithm = 'ShuffleSplit',
                    default = {'test_size': 0.33},
                    runtime = {'random_state': 'seed'},
                    required = {'n_splits': 1},
                    selected = True)},
            'encoder': {
                'backward': TechniqueDefinition(
                    name = 'backward',
                    module = 'category_encoders',
                    algorithm = 'BackwardDifferenceEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'basen': TechniqueDefinition(
                    name = 'basen',
                    module = 'category_encoders',
                    algorithm = 'BaseNEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'binary': TechniqueDefinition(
                    name = 'binary',
                    module = 'category_encoders',
                    algorithm = 'BinaryEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'dummy': TechniqueDefinition(
                    name = 'dummy',
                    module = 'category_encoders',
                    algorithm = 'OneHotEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'hashing': TechniqueDefinition(
                    name = 'hashing',
                    module = 'category_encoders',
                    algorithm = 'HashingEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'helmert': TechniqueDefinition(
                    name = 'helmert',
                    module = 'category_encoders',
                    algorithm = 'HelmertEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'james_stein': TechniqueDefinition(
                    name = 'james_stein',
                    module = 'category_encoders',
                    algorithm = 'JamesSteinEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'loo': TechniqueDefinition(
                    name = 'loo',
                    module = 'category_encoders',
                    algorithm = 'LeaveOneOutEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'm_estimate': TechniqueDefinition(
                    name = 'm_estimate',
                    module = 'category_encoders',
                    algorithm = 'MEstimateEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'ordinal': TechniqueDefinition(
                    name = 'ordinal',
                    module = 'category_encoders',
                    algorithm = 'OrdinalEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'polynomial': TechniqueDefinition(
                    name = 'polynomial_encoder',
                    module = 'category_encoders',
                    algorithm = 'PolynomialEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'sum': TechniqueDefinition(
                    name = 'sum',
                    module = 'category_encoders',
                    algorithm = 'SumEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'target': TechniqueDefinition(
                    name = 'target',
                    module = 'category_encoders',
                    algorithm = 'TargetEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'woe': TechniqueDefinition(
                    name = 'weight_of_evidence',
                    module = 'category_encoders',
                    algorithm = 'WOEEncoder',
                    data_dependent = {'cols': 'categoricals'})},
            'mixer': {
                'polynomial': TechniqueDefinition(
                    name = 'polynomial_mixer',
                    module = 'sklearn.preprocessing',
                    algorithm = 'PolynomialFeatures',
                    default = {
                        'degree': 2,
                        'interaction_only': True,
                        'include_bias': True}),
                'quotient': TechniqueDefinition(
                    name = 'quotient',
                    module = None,
                    algorithm = 'QuotientFeatures'),
                'sum': TechniqueDefinition(
                    name = 'sum',
                    module = None,
                    algorithm = 'SumFeatures'),
                'difference': TechniqueDefinition(
                    name = 'difference',
                    module = None,
                    algorithm = 'DifferenceFeatures')},
            'cleaver': {},
            'sampler': {
                'adasyn': TechniqueDefinition(
                    name = 'adasyn',
                    module = 'imblearn.over_sampling',
                    algorithm = 'ADASYN',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'}),
                'cluster': TechniqueDefinition(
                    name = 'cluster',
                    module = 'imblearn.under_sampling',
                    algorithm = 'ClusterCentroids',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'}),
                'knn': TechniqueDefinition(
                    name = 'knn',
                    module = 'imblearn.under_sampling',
                    algorithm = 'AllKNN',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'}),
                'near_miss': TechniqueDefinition(
                    name = 'near_miss',
                    module = 'imblearn.under_sampling',
                    algorithm = 'NearMiss',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'}),
                'random_over': TechniqueDefinition(
                    name = 'random_over',
                    module = 'imblearn.over_sampling',
                    algorithm = 'RandomOverSampler',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'}),
                'random_under': TechniqueDefinition(
                    name = 'random_under',
                    module = 'imblearn.under_sampling',
                    algorithm = 'RandomUnderSampler',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'}),
                'smote': TechniqueDefinition(
                    name = 'smote',
                    module = 'imblearn.over_sampling',
                    algorithm = 'SMOTE',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'}),
                'smotenc': TechniqueDefinition(
                    name = 'smotenc',
                    module = 'imblearn.over_sampling',
                    algorithm = 'SMOTENC',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'},
                    data_dependent = {
                        'categorical_features': 'categoricals_indices'}),
                'smoteenn': TechniqueDefinition(
                    name = 'smoteenn',
                    module = 'imblearn.combine',
                    algorithm = 'SMOTEENN',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'}),
                'smotetomek': TechniqueDefinition(
                    name = 'smotetomek',
                    module = 'imblearn.combine',
                    algorithm = 'SMOTETomek',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'})},
            'reducer': {
                'kbest': TechniqueDefinition(
                    name = 'kbest',
                    module = 'sklearn.feature_selection',
                    algorithm = 'SelectKBest',
                    default = {'k': 10, 'score_func': 'f_classif'},
                    selected = True),
                'fdr': TechniqueDefinition(
                    name = 'fdr',
                    module = 'sklearn.feature_selection',
                    algorithm = 'SelectFdr',
                    default = {'alpha': 0.05, 'score_func': 'f_classif'},
                    selected = True),
                'fpr': TechniqueDefinition(
                    name = 'fpr',
                    module = 'sklearn.feature_selection',
                    algorithm = 'SelectFpr',
                    default = {'alpha': 0.05, 'score_func': 'f_classif'},
                    selected = True),
                'custom': TechniqueDefinition(
                    name = 'custom',
                    module = 'sklearn.feature_selection',
                    algorithm = 'SelectFromModel',
                    default = {'threshold': 'mean'},
                    runtime = {'estimator': 'algorithm'},
                    selected = True),
                'rank': TechniqueDefinition(
                    name = 'rank',
                    module = 'simplify.critic.rank',
                    algorithm = 'RankSelect',
                    selected = True),
                'rfe': TechniqueDefinition(
                    name = 'rfe',
                    module = 'sklearn.feature_selection',
                    algorithm = 'RFE',
                    default = {'n_features_to_select': 10, 'step': 1},
                    runtime = {'estimator': 'algorithm'},
                    selected = True),
                'rfecv': TechniqueDefinition(
                    name = 'rfecv',
                    module = 'sklearn.feature_selection',
                    algorithm = 'RFECV',
                    default = {'n_features_to_select': 10, 'step': 1},
                    runtime = {'estimator': 'algorithm'},
                    selected = True)}}
        model_options = {
            'classify': {
                'adaboost': TechniqueDefinition(
                    name = 'adaboost',
                    module = 'sklearn.ensemble',
                    algorithm = 'AdaBoostClassifier'),
                'baseline_classifier': TechniqueDefinition(
                    name = 'baseline_classifier',
                    module = 'sklearn.dummy',
                    algorithm = 'DummyClassifier',
                    required = {'strategy': 'most_frequent'}),
                'logit': TechniqueDefinition(
                    name = 'logit',
                    module = 'sklearn.linear_model',
                    algorithm = 'LogisticRegression'),
                'random_forest': TechniqueDefinition(
                    name = 'random_forest',
                    module = 'sklearn.ensemble',
                    algorithm = 'RandomForestClassifier'),
                'svm_linear': TechniqueDefinition(
                    name = 'svm_linear',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'linear', 'probability': True}),
                'svm_poly': TechniqueDefinition(
                    name = 'svm_poly',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'poly', 'probability': True}),
                'svm_rbf': TechniqueDefinition(
                    name = 'svm_rbf',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'rbf', 'probability': True}),
                'svm_sigmoid': TechniqueDefinition(
                    name = 'svm_sigmoid ',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'sigmoid', 'probability': True}),
                'tensorflow': TechniqueDefinition(
                    name = 'tensorflow',
                    module = 'tensorflow',
                    algorithm = None,
                    default = {
                        'batch_size': 10,
                        'epochs': 2}),
                'xgboost': TechniqueDefinition(
                    name = 'xgboost',
                    module = 'xgboost',
                    algorithm = 'XGBClassifier',
                    data_dependent = 'scale_pos_weight')},
            'cluster': {
                'affinity': TechniqueDefinition(
                    name = 'affinity',
                    module = 'sklearn.cluster',
                    algorithm = 'AffinityPropagation'),
                'agglomerative': TechniqueDefinition(
                    name = 'agglomerative',
                    module = 'sklearn.cluster',
                    algorithm = 'AgglomerativeClustering'),
                'birch': TechniqueDefinition(
                    name = 'birch',
                    module = 'sklearn.cluster',
                    algorithm = 'Birch'),
                'dbscan': TechniqueDefinition(
                    name = 'dbscan',
                    module = 'sklearn.cluster',
                    algorithm = 'DBSCAN'),
                'kmeans': TechniqueDefinition(
                    name = 'kmeans',
                    module = 'sklearn.cluster',
                    algorithm = 'KMeans'),
                'mean_shift': TechniqueDefinition(
                    name = 'mean_shift',
                    module = 'sklearn.cluster',
                    algorithm = 'MeanShift'),
                'spectral': TechniqueDefinition(
                    name = 'spectral',
                    module = 'sklearn.cluster',
                    algorithm = 'SpectralClustering'),
                'svm_linear': TechniqueDefinition(
                    name = 'svm_linear',
                    module = 'sklearn.cluster',
                    algorithm = 'OneClassSVM'),
                'svm_poly': TechniqueDefinition(
                    name = 'svm_poly',
                    module = 'sklearn.cluster',
                    algorithm = 'OneClassSVM'),
                'svm_rbf': TechniqueDefinition(
                    name = 'svm_rbf',
                    module = 'sklearn.cluster',
                    algorithm = 'OneClassSVM,'),
                'svm_sigmoid': TechniqueDefinition(
                    name = 'svm_sigmoid',
                    module = 'sklearn.cluster',
                    algorithm = 'OneClassSVM')},
            'regress': {
                'adaboost': TechniqueDefinition(
                    name = 'adaboost',
                    module = 'sklearn.ensemble',
                    algorithm = 'AdaBoostRegressor'),
                'baseline_regressor': TechniqueDefinition(
                    name = 'baseline_regressor',
                    module = 'sklearn.dummy',
                    algorithm = 'DummyRegressor',
                    required = {'strategy': 'mean'}),
                'bayes_ridge': TechniqueDefinition(
                    name = 'bayes_ridge',
                    module = 'sklearn.linear_model',
                    algorithm = 'BayesianRidge'),
                'lasso': TechniqueDefinition(
                    name = 'lasso',
                    module = 'sklearn.linear_model',
                    algorithm = 'Lasso'),
                'lasso_lars': TechniqueDefinition(
                    name = 'lasso_lars',
                    module = 'sklearn.linear_model',
                    algorithm = 'LassoLars'),
                'ols': TechniqueDefinition(
                    name = 'ols',
                    module = 'sklearn.linear_model',
                    algorithm = 'LinearRegression'),
                'random_forest': TechniqueDefinition(
                    name = 'random_forest',
                    module = 'sklearn.ensemble',
                    algorithm = 'RandomForestRegressor'),
                'ridge': TechniqueDefinition(
                    name = 'ridge',
                    module = 'sklearn.linear_model',
                    algorithm = 'Ridge'),
                'svm_linear': TechniqueDefinition(
                    name = 'svm_linear',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'linear', 'probability': True}),
                'svm_poly': TechniqueDefinition(
                    name = 'svm_poly',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'poly', 'probability': True}),
                'svm_rbf': TechniqueDefinition(
                    name = 'svm_rbf',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'rbf', 'probability': True}),
                'svm_sigmoid': TechniqueDefinition(
                    name = 'svm_sigmoid ',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'sigmoid', 'probability': True}),
                'xgboost': TechniqueDefinition(
                    name = 'xgboost',
                    module = 'xgboost',
                    algorithm = 'XGBRegressor',
                    data_dependent = 'scale_pos_weight')}}
        gpu_options = {
            'classify': {
                'forest_inference': TechniqueDefinition(
                    name = 'forest_inference',
                    module = 'cuml',
                    algorithm = 'ForestInference'),
                'random_forest': TechniqueDefinition(
                    name = 'random_forest',
                    module = 'cuml',
                    algorithm = 'RandomForestClassifier'),
                'logit': TechniqueDefinition(
                    name = 'logit',
                    module = 'cuml',
                    algorithm = 'LogisticRegression')},
            'cluster': {
                'dbscan': TechniqueDefinition(
                    name = 'dbscan',
                    module = 'cuml',
                    algorithm = 'DBScan'),
                'kmeans': TechniqueDefinition(
                    name = 'kmeans',
                    module = 'cuml',
                    algorithm = 'KMeans')},
            'regressor': {
                'lasso': TechniqueDefinition(
                    name = 'lasso',
                    module = 'cuml',
                    algorithm = 'Lasso'),
                'ols': TechniqueDefinition(
                    name = 'ols',
                    module = 'cuml',
                    algorithm = 'LinearRegression'),
                'ridge': TechniqueDefinition(
                    name = 'ridge',
                    module = 'cuml',
                    algorithm = 'RidgeRegression')}}
        self.contents['modeler'] = model_options[
            self.project.idea['chef']['model_type']]
        if self.project.idea['general']['gpu']:
            self.contents['modeler'].update(
                gpu_options[idea['chef']['model_type']])
        return self
