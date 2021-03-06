"""
.. module:: analyst
:synopsis: machine learning made simple
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from copy import deepcopy
from dataclasses import dataclass
from dataclasses import field
from functools import wraps
from inspect import signature
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Optional,
    Tuple, Union)

import numpy as np
import pandas as pd
from scipy.stats import randint, uniform
from sklearn.utils import check_X_y
from sklearn.utils.validation import check_is_fitted

from simplify.analyst import algorithms
from simplify.core.book import Book
from simplify.core.book import Chapter
from simplify.core.book import Technique
from simplify.core.creators import Publisher
from simplify.core.repository import Repository
from simplify.core.scholar import Scholar
from simplify.core.utilities import listify


""" Book Subclass """

@dataclass
class Cookbook(Book):
    """Standard class for iterable storage in the Analyst subpackage.

    Args:
        name (Optional[str]): designates the name of the class used for internal
            referencing throughout siMpLify. If the class needs settings from
            the shared Idea instance, 'name' should match the appropriate
            section name in Idea. When subclassing, it is a good idea to use
            the same 'name' attribute as the base class for effective
            coordination between siMpLify classes. 'name' is used instead of
            __class__.__name__ to make such subclassing easier. Defaults to
            'cookbook'
        chapters (Optional[List['Chapter']]): iterable collection of steps and
            techniques to apply at each step. Defaults to an empty list.
        _iterable(Optional[str]): name of property to store alternative proxy
            to 'recipes'.

    """
    name: Optional[str] = field(default_factory = lambda: 'cookbook')
    chapters: Optional[List['Chapter']] = field(default_factory = list)
    _iterable: Optional[str] = field(default_factory = lambda: 'recipes')

""" Technique Subclass and Decorator """

def numpy_shield(callable: Callable) -> Callable:
    """
    """
    @wraps(callable)
    def wrapper(*args, **kwargs):
        call_signature = signature(callable)
        arguments = dict(call_signature.bind(*args, **kwargs).arguments)
        try:
            x_columns = list(arguments['x'].columns.values)
            result = callable(*args, **kwargs)
            if isinstance(result, np.ndarray):
                result = pd.DataFrame(result, columns = x_columns)
        except KeyError:
            result = callable(*args, **kwargs)
        return result
    return wrapper


@dataclass
class AnalystTechnique(Technique):
    """

    Args:


    """
    name: Optional[str] = None
    step: Optional[str] = None
    module: Optional[str]
    algorithm: Optional[object] = None
    parameters: Optional[Dict[str, Any]] = field(default_factory = dict)
    default: Optional[Dict[str, Any]] = field(default_factory = dict)
    required: Optional[Dict[str, Any]] = field(default_factory = dict)
    runtime: Optional[Dict[str, str]] = field(default_factory = dict)
    selected: Optional[Union[bool, List[str]]] = False
    data_dependent: Optional[Dict[str, str]] = field(default_factory = dict)
    parameter_space: Optional[Dict[str, List[Union[int, float]]]] = field(
        default_factory = dict)
    fit_method: Optional[str] = field(default_factory = lambda: 'fit')
    transform_method: Optional[str] = field(
        default_factory = lambda: 'transform')

    """ Core siMpLify Methods """

    def apply(self, data: 'Dataset') -> 'Dataset':
        if data.stages.current in ['full']:
            self.fit(x = data.x, y = data.y)
            data.x = self.transform(x = data.x, y = data.y)
        else:
            self.fit(x = data.x_train, y = data.y_train)
            data.x_train = self.transform(x = data.x_train, y = data.y_train)
            data.x_test = self.transform(x = data.x_test, y = data.y_test)
        return data

    """ Scikit-Learn Compatibility Methods """

    @numpy_shield
    def fit(self,
            x: Optional[Union[pd.DataFrame, np.ndarray]] = None,
            y: Optional[Union[pd.Series, np.ndarray]] = None) -> None:
        """Generic fit method for partial compatibility to sklearn.

        Args:
            x (Optional[Union[pd.DataFrame, np.ndarray]]): independent
                variables/features.
            y (Optional[Union[pd.Series, np.ndarray]]): dependent
                variable/label.

        Raises:
            AttributeError if no 'fit' method exists for 'technique'.

        """
        x, y = check_X_y(X = x, y = y, accept_sparse = True)
        if self.fit_method is not None:
            if y is None:
                getattr(self.algorithm, self.fit_method)(x)
            else:
                self.algorithm = self.algorithm.fit(x, y)
        return self

    @numpy_shield
    def transform(self,
            x: Optional[Union[pd.DataFrame, np.ndarray]] = None,
            y: Optional[Union[pd.Series, np.ndarray]] = None) -> pd.DataFrame:
        """Generic transform method for partial compatibility to sklearn.

        Args:
            x (Optional[Union[pd.DataFrame, np.ndarray]]): independent
                variables/features.
            y (Optional[Union[pd.Series, np.ndarray]]): dependent
                variable/label.

        Returns:
            transformed x or data, depending upon what is passed to the
                method.

        Raises:
            AttributeError if no 'transform' method exists for local
                'process'.

        """
        if self.transform_method is not None:
            try:
                return getattr(self.algorithm, self.transform_method)(x)
            except AttributeError:
                return x
        else:
            return x


""" Publisher Subclass """

@dataclass
class AnalystPublisher(Publisher):
    """Creates 'Cookbook'

    Args:
        idea ('Idea'): an 'Idea' instance with project settings.

    """
    idea: 'Idea'

    """ Public Methods """

    # def add_cleaves(self,
    #         cleave_group: str,
    #         prefixes: Union[List[str], str] = None,
    #         columns: Union[List[str], str] = None) -> None:
    #     """Adds cleaves to the list of cleaves.

    #     Args:
    #         cleave_group (str): names the set of features in the group.
    #         prefixes (Union[List[str], str]): name(s) of prefixes to columns to
    #             be included within the cleave.
    #         columns (Union[List[str], str]): name(s) of columns to be included
    #             within the cleave.

    #     """
    #     # if not self._exists('cleaves'):
    #     #     self.cleaves = []
    #     # columns = self.dataset.make_column_list(
    #     #     prefixes = prefixes,
    #     #     columns = columns)
    #     # self.workers['cleaver'].add_techniques(
    #     #     cleave_group = cleave_group,
    #     #     columns = columns)
    #     # self.cleaves.append(cleave_group)
    #     return self


""" Scholar Subclass """

@dataclass
class Analyst(Scholar):
    """Applies a 'Cookbook' instance to data.

    Args:
        idea (ClassVar['Idea']): an 'Idea' instance with project settings.

    """
    idea: ClassVar['Idea']

    """ Private Methods """

    def _finalize_chapters(self, book: 'Book', data: 'Dataset') -> 'Book':
        """Finalizes 'Chapter' instances in 'Book'.

        Args:
            book ('Book'): instance containing 'chapters' with 'techniques' that
                have 'data_dependent' and/or 'conditional' 'parameters' to
                add.
            data ('Dataset): instance with potential information to use to
                finalize 'parameters' for 'book'.

        Returns:
            'Book': with any necessary modofications made.

        """
        for chapter in book.chapters:
            new_techniques = []
            for technique in chapter.techniques:
                if not technique.name in ['none']:
                    new_technique = self._add_conditionals(
                        book = book,
                        technique = technique,
                        data = data)
                    new_technique = self._add_data_dependent(
                        technique = technique,
                        data = data)
                    new_techniques.append(self._add_parameters_to_algorithm(
                        technique = technique))
            chapter.techniques = new_techniques
        return book

    def _apply_chapter(self,
            chapter: 'Chapter',
            data: Union['Dataset']) -> 'Chapter':
        """Applies a 'chapter' of 'steps' to 'data'.

        Args:
            chapter ('Chapter'): instance with 'steps' to apply to 'data'.
            data (Union['Dataset', 'Book']): object for 'chapter' to be applied.

        Return:
            'Chapter': with any changes made. Modified 'data' is added to the
                'Chapter' instance with the attribute name matching the 'name'
                attribute of 'data'.

        """
        data.create_xy()
        for i, technique in enumerate(chapter.techniques):
            if technique.step in ['split']:
                chapter, data = self._split_loop(
                    chapter = chapter,
                    index = i,
                    data = data)
                break
            elif technique.step in ['search']:
                remaining = self._search_loop(
                    steps = remaining,
                    index = i,
                    data = data)
                data = technique.apply(data = data)
            elif not technique.name in ['none', None]:
                data = technique.apply(data = data)
        setattr(chapter, 'data', data)
        return chapter

    def _split_loop(self,
            chapter: 'Chapter',
            index: int,
            data: 'DataSet') -> ('Chapter', 'Dataset'):
        """Splits 'data' and applies remaining steps in 'chapter'.

        Args:
            chapter ('Chapter'): instance with 'steps' to apply to 'data'.
            index (int): number of step in 'chapter' 'steps' where split method
                is located. All subsequent steps are completed with data split
                into training and testing sets.
            data ('Dataset'): data object for 'chapter' to be applied.

        Return:
            'Chapter', 'Dataset': with any changes made.

        """
        data.stages.change('testing')
        split_algorithm = chapter.techniques[index].algorithm
        for train_index, test_index in split_algorithm.split(data.x, data.y):
            data.x_train = data.x.iloc[train_index]
            data.x_test = data.x.iloc[test_index]
            data.y_train = data.y[train_index]
            data.y_test = data.y[test_index]
            for technique in chapter.techniques[index + 1:]:
                if not technique.name in ['none', None]:
                    data = technique.apply(data = data)
        return chapter, data

    def _search_loop(self,
            chapter: 'Chapter',
            index: int,
            data: 'DataSet') -> ('Chapter', 'Dataset'):
        """Searches hyperparameters for a particular 'algorithm'.

        Args:
            chapter ('Chapter'): instance with 'steps' to apply to 'data'.
            index (int): number of step in 'chapter' 'steps' where the search
                method should be applied
            data ('Dataset'): data object for 'chapter' to be applied.

        Return:
            'Chapter': with the searched step modified with the best found
                hyperparameters.

        """
        return chapter

    def _add_model_conditionals(self,
            technique: 'Technique',
            data: 'Dataset') -> 'Technique':
        """Adds any conditional parameters to 'technique'

        Args:
            technique ('Technique'): an instance with 'algorithm' and
                'parameters' not yet combined.
            data ('Dataset'): data object used to derive hyperparameters.

        Returns:
            'Technique': with any applicable parameters added.

        """
        self._model_calculate_hyperparameters(
            technique = technique,
            data = data)
        if technique.name in ['xgboost'] and self.idea['general']['gpu']:
            technique.parameters['tree_method'] = 'gpu_exact'
        elif step in ['tensorflow']:
            technique.algorithm = algorithms.make_tensorflow_model(
                technique = technique,
                data = data)
        return technique

    def _model_calculate_hyperparameters(self,
            technique: 'Technique',
            data: 'Dataset') -> 'Technique':
        """Computes hyperparameters from data.

        This method will include any heuristics or methods for creating smart
        algorithm parameters (without creating data leakage problems).

        This method currently only support xgboost's scale_pos_weight
        parameter. Future hyperparameter computations will be added as they
        are discovered.

        Args:
            technique ('Technique'): an instance with 'algorithm' and
                'parameters' not yet combined.
            data ('Dataset'): data object used to derive hyperparameters.

        Returns:
            'Technique': with any applicable parameters added.

        """
        if (technique.name in ['xgboost']
                and self.idea['analyst']['calculate_hyperparameters']):
            technique.parameters['scale_pos_weight'] = (
                    len(self.data['y'].index) /
                    ((self.data['y'] == 1).sum())) - 1
        return self


""" Options """

@dataclass
class Tools(Repository):
    """A dictonary of AnalystTechnique options for the Analyst subpackage.

    Args:
        idea (ClassVar['Idea']): shared 'Idea' instance with project settings.

    """
    idea: ClassVar['Idea']

    def create(self) -> None:
        self.contents = {
            'fill': {
                'defaults': AnalystTechnique(
                    name = 'defaults',
                    module = 'simplify.analyst.algorithms',
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
                'impute': AnalystTechnique(
                    name = 'defaults',
                    module = 'sklearn.impute',
                    algorithm = 'SimpleImputer',
                    default = {'defaults': {}}),
                'knn_impute': AnalystTechnique(
                    name = 'defaults',
                    module = 'sklearn.impute',
                    algorithm = 'KNNImputer',
                    default = {'defaults': {}})},
            'categorize': {
                'automatic': AnalystTechnique(
                    name = 'automatic',
                    module = 'simplify.analyst.algorithms',
                    algorithm = 'auto_categorize',
                    default = {'threshold': 10}),
                'binary': AnalystTechnique(
                    name = 'binary',
                    module = 'sklearn.preprocessing',
                    algorithm = 'Binarizer',
                    default = {'threshold': 0.5}),
                'bins': AnalystTechnique(
                    name = 'bins',
                    module = 'sklearn.preprocessing',
                    algorithm = 'KBinsDiscretizer',
                    default = {
                        'strategy': 'uniform',
                        'n_bins': 5},
                    selected = True,
                    required = {'encode': 'onehot'})},
            'scale': {
                'gauss': AnalystTechnique(
                    name = 'gauss',
                    module = None,
                    algorithm = 'Gaussify',
                    default = {'standardize': False, 'copy': False},
                    selected = True,
                    required = {'rescaler': 'standard'}),
                'maxabs': AnalystTechnique(
                    name = 'maxabs',
                    module = 'sklearn.preprocessing',
                    algorithm = 'MaxAbsScaler',
                    default = {'copy': False},
                    selected = True),
                'minmax': AnalystTechnique(
                    name = 'minmax',
                    module = 'sklearn.preprocessing',
                    algorithm = 'MinMaxScaler',
                    default = {'copy': False},
                    selected = True),
                'normalize': AnalystTechnique(
                    name = 'normalize',
                    module = 'sklearn.preprocessing',
                    algorithm = 'Normalizer',
                    default = {'copy': False},
                    selected = True),
                'quantile': AnalystTechnique(
                    name = 'quantile',
                    module = 'sklearn.preprocessing',
                    algorithm = 'QuantileTransformer',
                    default = {'copy': False},
                    selected = True),
                'robust': AnalystTechnique(
                    name = 'robust',
                    module = 'sklearn.preprocessing',
                    algorithm = 'RobustScaler',
                    default = {'copy': False},
                    selected = True),
                'standard': AnalystTechnique(
                    name = 'standard',
                    module = 'sklearn.preprocessing',
                    algorithm = 'StandardScaler',
                    default = {'copy': False},
                    selected = True)},
            'split': {
                'group_kfold': AnalystTechnique(
                    name = 'group_kfold',
                    module = 'sklearn.model_selection',
                    algorithm = 'GroupKFold',
                    default = {'n_splits': 5},
                    runtime = {'random_state': 'seed'},
                    selected = True,
                    fit_method = None,
                    transform_method = 'split'),
                'kfold': AnalystTechnique(
                    name = 'kfold',
                    module = 'sklearn.model_selection',
                    algorithm = 'KFold',
                    default = {'n_splits': 5, 'shuffle': False},
                    runtime = {'random_state': 'seed'},
                    selected = True,
                    required = {'shuffle': True},
                    fit_method = None,
                    transform_method = 'split'),
                'stratified': AnalystTechnique(
                    name = 'stratified',
                    module = 'sklearn.model_selection',
                    algorithm = 'StratifiedKFold',
                    default = {'n_splits': 5, 'shuffle': False},
                    runtime = {'random_state': 'seed'},
                    selected = True,
                    required = {'shuffle': True},
                    fit_method = None,
                    transform_method = 'split'),
                'time': AnalystTechnique(
                    name = 'time',
                    module = 'sklearn.model_selection',
                    algorithm = 'TimeSeriesSplit',
                    default = {'n_splits': 5},
                    runtime = {'random_state': 'seed'},
                    selected = True,
                    fit_method = None,
                    transform_method = 'split'),
                'train_test': AnalystTechnique(
                    name = 'train_test',
                    module = 'sklearn.model_selection',
                    algorithm = 'ShuffleSplit',
                    default = {'test_size': 0.33},
                    runtime = {'random_state': 'seed'},
                    required = {'n_splits': 1},
                    selected = True,
                    fit_method = None,
                    transform_method = 'split')},
            'encode': {
                'backward': AnalystTechnique(
                    name = 'backward',
                    module = 'category_encoders',
                    algorithm = 'BackwardDifferenceEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'basen': AnalystTechnique(
                    name = 'basen',
                    module = 'category_encoders',
                    algorithm = 'BaseNEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'binary': AnalystTechnique(
                    name = 'binary',
                    module = 'category_encoders',
                    algorithm = 'BinaryEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'dummy': AnalystTechnique(
                    name = 'dummy',
                    module = 'category_encoders',
                    algorithm = 'OneHotEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'hashing': AnalystTechnique(
                    name = 'hashing',
                    module = 'category_encoders',
                    algorithm = 'HashingEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'helmert': AnalystTechnique(
                    name = 'helmert',
                    module = 'category_encoders',
                    algorithm = 'HelmertEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'james_stein': AnalystTechnique(
                    name = 'james_stein',
                    module = 'category_encoders',
                    algorithm = 'JamesSteinEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'loo': AnalystTechnique(
                    name = 'loo',
                    module = 'category_encoders',
                    algorithm = 'LeaveOneOutEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'm_estimate': AnalystTechnique(
                    name = 'm_estimate',
                    module = 'category_encoders',
                    algorithm = 'MEstimateEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'ordinal': AnalystTechnique(
                    name = 'ordinal',
                    module = 'category_encoders',
                    algorithm = 'OrdinalEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'polynomial': AnalystTechnique(
                    name = 'polynomial_encoder',
                    module = 'category_encoders',
                    algorithm = 'PolynomialEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'sum': AnalystTechnique(
                    name = 'sum',
                    module = 'category_encoders',
                    algorithm = 'SumEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'target': AnalystTechnique(
                    name = 'target',
                    module = 'category_encoders',
                    algorithm = 'TargetEncoder',
                    data_dependent = {'cols': 'categoricals'}),
                'woe': AnalystTechnique(
                    name = 'weight_of_evidence',
                    module = 'category_encoders',
                    algorithm = 'WOEEncoder',
                    data_dependent = {'cols': 'categoricals'})},
            'mix': {
                'polynomial': AnalystTechnique(
                    name = 'polynomial_mixer',
                    module = 'sklearn.preprocessing',
                    algorithm = 'PolynomialFeatures',
                    default = {
                        'degree': 2,
                        'interaction_only': True,
                        'include_bias': True}),
                'quotient': AnalystTechnique(
                    name = 'quotient',
                    module = None,
                    algorithm = 'QuotientFeatures'),
                'sum': AnalystTechnique(
                    name = 'sum',
                    module = None,
                    algorithm = 'SumFeatures'),
                'difference': AnalystTechnique(
                    name = 'difference',
                    module = None,
                    algorithm = 'DifferenceFeatures')},
            'cleave': {
                'cleaver': AnalystTechnique(
                    name = 'cleaver',
                    module = 'simplify.analyst.algorithms',
                    algorithm = 'Cleaver')},
            'sample': {
                'adasyn': AnalystTechnique(
                    name = 'adasyn',
                    module = 'imblearn.over_sampling',
                    algorithm = 'ADASYN',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'},
                    fit_method = None,
                    transform_method = 'fit_resample'),
                'cluster': AnalystTechnique(
                    name = 'cluster',
                    module = 'imblearn.under_sampling',
                    algorithm = 'ClusterCentroids',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'},
                    fit_method = None,
                    transform_method = 'fit_resample'),
                'knn': AnalystTechnique(
                    name = 'knn',
                    module = 'imblearn.under_sampling',
                    algorithm = 'AllKNN',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'},
                    fit_method = None,
                    transform_method = 'fit_resample'),
                'near_miss': AnalystTechnique(
                    name = 'near_miss',
                    module = 'imblearn.under_sampling',
                    algorithm = 'NearMiss',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'},
                    fit_method = None,
                    transform_method = 'fit_resample'),
                'random_over': AnalystTechnique(
                    name = 'random_over',
                    module = 'imblearn.over_sampling',
                    algorithm = 'RandomOverSampler',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'},
                    fit_method = None,
                    transform_method = 'fit_resample'),
                'random_under': AnalystTechnique(
                    name = 'random_under',
                    module = 'imblearn.under_sampling',
                    algorithm = 'RandomUnderSampler',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'},
                    fit_method = None,
                    transform_method = 'fit_resample'),
                'smote': AnalystTechnique(
                    name = 'smote',
                    module = 'imblearn.over_sampling',
                    algorithm = 'SMOTE',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'},
                    fit_method = None,
                    transform_method = 'fit_resample'),
                'smotenc': AnalystTechnique(
                    name = 'smotenc',
                    module = 'imblearn.over_sampling',
                    algorithm = 'SMOTENC',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'},
                    data_dependent = {
                        'categorical_features': 'categoricals_indices'},
                    fit_method = None,
                    transform_method = 'fit_resample'),
                'smoteenn': AnalystTechnique(
                    name = 'smoteenn',
                    module = 'imblearn.combine',
                    algorithm = 'SMOTEENN',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'},
                    fit_method = None,
                    transform_method = 'fit_resample'),
                'smotetomek': AnalystTechnique(
                    name = 'smotetomek',
                    module = 'imblearn.combine',
                    algorithm = 'SMOTETomek',
                    default = {'sampling_strategy': 'auto'},
                    runtime = {'random_state': 'seed'},
                    fit_method = None,
                    transform_method = 'fit_resample')},
            'reduce': {
                'kbest': AnalystTechnique(
                    name = 'kbest',
                    module = 'sklearn.feature_selection',
                    algorithm = 'SelectKBest',
                    default = {'k': 10, 'score_func': 'f_classif'},
                    selected = True),
                'fdr': AnalystTechnique(
                    name = 'fdr',
                    module = 'sklearn.feature_selection',
                    algorithm = 'SelectFdr',
                    default = {'alpha': 0.05, 'score_func': 'f_classif'},
                    selected = True),
                'fpr': AnalystTechnique(
                    name = 'fpr',
                    module = 'sklearn.feature_selection',
                    algorithm = 'SelectFpr',
                    default = {'alpha': 0.05, 'score_func': 'f_classif'},
                    selected = True),
                'custom': AnalystTechnique(
                    name = 'custom',
                    module = 'sklearn.feature_selection',
                    algorithm = 'SelectFromModel',
                    default = {'threshold': 'mean'},
                    runtime = {'estimator': 'algorithm'},
                    selected = True),
                'rank': AnalystTechnique(
                    name = 'rank',
                    module = 'simplify.critic.rank',
                    algorithm = 'RankSelect',
                    selected = True),
                'rfe': AnalystTechnique(
                    name = 'rfe',
                    module = 'sklearn.feature_selection',
                    algorithm = 'RFE',
                    default = {'n_features_to_select': 10, 'step': 1},
                    runtime = {'estimator': 'algorithm'},
                    selected = True),
                'rfecv': AnalystTechnique(
                    name = 'rfecv',
                    module = 'sklearn.feature_selection',
                    algorithm = 'RFECV',
                    default = {'n_features_to_select': 10, 'step': 1},
                    runtime = {'estimator': 'algorithm'},
                    selected = True)}}
        model_options = {
            'classify': {
                'adaboost': AnalystTechnique(
                    name = 'adaboost',
                    module = 'sklearn.ensemble',
                    algorithm = 'AdaBoostClassifier',
                    transform_method = None),
                'baseline_classifier': AnalystTechnique(
                    name = 'baseline_classifier',
                    module = 'sklearn.dummy',
                    algorithm = 'DummyClassifier',
                    required = {'strategy': 'most_frequent'},
                    transform_method = None),
                'logit': AnalystTechnique(
                    name = 'logit',
                    module = 'sklearn.linear_model',
                    algorithm = 'LogisticRegression',
                    transform_method = None),
                'random_forest': AnalystTechnique(
                    name = 'random_forest',
                    module = 'sklearn.ensemble',
                    algorithm = 'RandomForestClassifier',
                    transform_method = None),
                'svm_linear': AnalystTechnique(
                    name = 'svm_linear',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'linear', 'probability': True},
                    transform_method = None),
                'svm_poly': AnalystTechnique(
                    name = 'svm_poly',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'poly', 'probability': True},
                    transform_method = None),
                'svm_rbf': AnalystTechnique(
                    name = 'svm_rbf',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'rbf', 'probability': True},
                    transform_method = None),
                'svm_sigmoid': AnalystTechnique(
                    name = 'svm_sigmoid ',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'sigmoid', 'probability': True},
                    transform_method = None),
                'tensorflow': AnalystTechnique(
                    name = 'tensorflow',
                    module = 'tensorflow',
                    algorithm = None,
                    default = {
                        'batch_size': 10,
                        'epochs': 2},
                    transform_method = None),
                'xgboost': AnalystTechnique(
                    name = 'xgboost',
                    module = 'xgboost',
                    algorithm = 'XGBClassifier',
                    # data_dependent = 'scale_pos_weight',
                    transform_method = None)},
            'cluster': {
                'affinity': AnalystTechnique(
                    name = 'affinity',
                    module = 'sklearn.cluster',
                    algorithm = 'AffinityPropagation',
                    transform_method = None),
                'agglomerative': AnalystTechnique(
                    name = 'agglomerative',
                    module = 'sklearn.cluster',
                    algorithm = 'AgglomerativeClustering',
                    transform_method = None),
                'birch': AnalystTechnique(
                    name = 'birch',
                    module = 'sklearn.cluster',
                    algorithm = 'Birch',
                    transform_method = None),
                'dbscan': AnalystTechnique(
                    name = 'dbscan',
                    module = 'sklearn.cluster',
                    algorithm = 'DBSCAN',
                    transform_method = None),
                'kmeans': AnalystTechnique(
                    name = 'kmeans',
                    module = 'sklearn.cluster',
                    algorithm = 'KMeans',
                    transform_method = None),
                'mean_shift': AnalystTechnique(
                    name = 'mean_shift',
                    module = 'sklearn.cluster',
                    algorithm = 'MeanShift',
                    transform_method = None),
                'spectral': AnalystTechnique(
                    name = 'spectral',
                    module = 'sklearn.cluster',
                    algorithm = 'SpectralClustering',
                    transform_method = None),
                'svm_linear': AnalystTechnique(
                    name = 'svm_linear',
                    module = 'sklearn.cluster',
                    algorithm = 'OneClassSVM',
                    transform_method = None),
                'svm_poly': AnalystTechnique(
                    name = 'svm_poly',
                    module = 'sklearn.cluster',
                    algorithm = 'OneClassSVM',
                    transform_method = None),
                'svm_rbf': AnalystTechnique(
                    name = 'svm_rbf',
                    module = 'sklearn.cluster',
                    algorithm = 'OneClassSVM,',
                    transform_method = None),
                'svm_sigmoid': AnalystTechnique(
                    name = 'svm_sigmoid',
                    module = 'sklearn.cluster',
                    algorithm = 'OneClassSVM',
                    transform_method = None)},
            'regress': {
                'adaboost': AnalystTechnique(
                    name = 'adaboost',
                    module = 'sklearn.ensemble',
                    algorithm = 'AdaBoostRegressor',
                    transform_method = None),
                'baseline_regressor': AnalystTechnique(
                    name = 'baseline_regressor',
                    module = 'sklearn.dummy',
                    algorithm = 'DummyRegressor',
                    required = {'strategy': 'mean'},
                    transform_method = None),
                'bayes_ridge': AnalystTechnique(
                    name = 'bayes_ridge',
                    module = 'sklearn.linear_model',
                    algorithm = 'BayesianRidge',
                    transform_method = None),
                'lasso': AnalystTechnique(
                    name = 'lasso',
                    module = 'sklearn.linear_model',
                    algorithm = 'Lasso',
                    transform_method = None),
                'lasso_lars': AnalystTechnique(
                    name = 'lasso_lars',
                    module = 'sklearn.linear_model',
                    algorithm = 'LassoLars',
                    transform_method = None),
                'ols': AnalystTechnique(
                    name = 'ols',
                    module = 'sklearn.linear_model',
                    algorithm = 'LinearRegression',
                    transform_method = None),
                'random_forest': AnalystTechnique(
                    name = 'random_forest',
                    module = 'sklearn.ensemble',
                    algorithm = 'RandomForestRegressor',
                    transform_method = None),
                'ridge': AnalystTechnique(
                    name = 'ridge',
                    module = 'sklearn.linear_model',
                    algorithm = 'Ridge',
                    transform_method = None),
                'svm_linear': AnalystTechnique(
                    name = 'svm_linear',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'linear', 'probability': True},
                    transform_method = None),
                'svm_poly': AnalystTechnique(
                    name = 'svm_poly',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'poly', 'probability': True},
                    transform_method = None),
                'svm_rbf': AnalystTechnique(
                    name = 'svm_rbf',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'rbf', 'probability': True},
                    transform_method = None),
                'svm_sigmoid': AnalystTechnique(
                    name = 'svm_sigmoid ',
                    module = 'sklearn.svm',
                    algorithm = 'SVC',
                    required = {'kernel': 'sigmoid', 'probability': True},
                    transform_method = None),
                'xgboost': AnalystTechnique(
                    name = 'xgboost',
                    module = 'xgboost',
                    algorithm = 'XGBRegressor',
                    # data_dependent = 'scale_pos_weight',
                    transform_method = None)}}
        gpu_options = {
            'classify': {
                'forest_inference': AnalystTechnique(
                    name = 'forest_inference',
                    module = 'cuml',
                    algorithm = 'ForestInference',
                    transform_method = None),
                'random_forest': AnalystTechnique(
                    name = 'random_forest',
                    module = 'cuml',
                    algorithm = 'RandomForestClassifier',
                    transform_method = None),
                'logit': AnalystTechnique(
                    name = 'logit',
                    module = 'cuml',
                    algorithm = 'LogisticRegression',
                    transform_method = None)},
            'cluster': {
                'dbscan': AnalystTechnique(
                    name = 'dbscan',
                    module = 'cuml',
                    algorithm = 'DBScan',
                    transform_method = None),
                'kmeans': AnalystTechnique(
                    name = 'kmeans',
                    module = 'cuml',
                    algorithm = 'KMeans',
                    transform_method = None)},
            'regressor': {
                'lasso': AnalystTechnique(
                    name = 'lasso',
                    module = 'cuml',
                    algorithm = 'Lasso',
                    transform_method = None),
                'ols': AnalystTechnique(
                    name = 'ols',
                    module = 'cuml',
                    algorithm = 'LinearRegression',
                    transform_method = None),
                'ridge': AnalystTechnique(
                    name = 'ridge',
                    module = 'cuml',
                    algorithm = 'RidgeRegression',
                    transform_method = None)}}
        self.contents['model'] = model_options[
            self.idea['analyst']['model_type']]
        if self.idea['general']['gpu']:
            self.contents['model'].update(
                gpu_options[idea['analyst']['model_type']])
        return self.contents