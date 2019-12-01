"""
.. module:: modeler
:synopsis: applies machine learning and statistical models to data
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

from simplify.core.contributor import SimpleContributor
from simplify.core.contributor import Outline


@dataclass
class Modeler(SimpleContributor):
    """Applies machine learning or statistical model to data.

    Args:
        name (Optional[str]): designates the name of the class used for internal
            referencing throughout siMpLify. If the class needs settings from
            the shared Idea instance, 'name' should match the appropriate
            section name in Idea. When subclassing, it is a good idea to use
            the same 'name' attribute as the base class for effective
            coordination between siMpLify classes. 'name' is used instead of
            __class__.__name__ to make such subclassing easier. If 'name' is not
            provided, __class__.__name__.lower() is used instead.

    """
    name: str = 'modeler'

    def __post_init__(self) -> None:
        super().__post_init__()
        return self

    """ Private Methods """

    def _add_gpu_steps_classify(self) -> None:
        self.options.update({
            'forest_inference': Outline(
                name = 'forest_inference',
                module = 'cuml',
                algorithm = 'ForestInference'),
            'random_forest': Outline(
                name = 'random_forest',
                module = 'cuml',
                algorithm = 'RandomForestClassifier'),
            'logit': Outline(
                name = 'logit',
                module = 'cuml',
                algorithm = 'LogisticRegression')})
        return self

    def _add_gpu_steps_cluster(self) -> None:
        self.options.update({
            'dbscan': Outline(
                name = 'dbscan',
                module = 'cuml',
                algorithm = 'DBScan'),
            'kmeans': Outline(
                name = 'kmeans',
                module = 'cuml',
                algorithm = 'KMeans')})
        return self

    def _add_gpu_steps_regress(self) -> None:
        self.options.update({
            'lasso': Outline(
                name = 'lasso',
                module = 'cuml',
                algorithm = 'Lasso'),
            'ols': Outline(
                name = 'ols',
                module = 'cuml',
                algorithm = 'LinearRegression'),
            'ridge': Outline(
                name = 'ridge',
                module = 'cuml',
                algorithm = 'RidgeRegression')})
        return self

    def _draft_classify(self) -> None:
        self.options = {
            'adaboost': Outline(
                name = 'adaboost',
                module = 'sklearn.ensemble',
                algorithm = 'AdaBoostClassifier'),
            'baseline_classifier': Outline(
                name = 'baseline_classifier',
                module = 'sklearn.dummy',
                algorithm = 'DummyClassifier',
                required = {'strategy': 'most_frequent'}),
            'logit': Outline(
                name = 'logit',
                module = 'sklearn.linear_model',
                algorithm = 'LogisticRegression'),
            'random_forest': Outline(
                name = 'random_forest',
                module = 'sklearn.ensemble',
                algorithm = 'RandomForestClassifier'),
            'svm_linear': Outline(
                name = 'svm_linear',
                module = 'sklearn.svm',
                algorithm = 'SVC',
                required = {'kernel': 'linear', 'probability': True}),
            'svm_poly': Outline(
                name = 'svm_poly',
                module = 'sklearn.svm',
                algorithm = 'SVC',
                required = {'kernel': 'poly', 'probability': True}),
            'svm_rbf': Outline(
                name = 'svm_rbf',
                module = 'sklearn.svm',
                algorithm = 'SVC',
                required = {'kernel': 'rbf', 'probability': True}),
            'svm_sigmoid': Outline(
                name = 'svm_sigmoid ',
                module = 'sklearn.svm',
                algorithm = 'SVC',
                required = {'kernel': 'sigmoid', 'probability': True}),
            'tensorflow': Outline(
                name = 'tensorflow',
                module = 'tensorflow',
                algorithm = None,
                default = {
                    'batch_size': 10,
                    'epochs': 2}),
            'xgboost': Outline(
                name = 'xgboost',
                module = 'xgboost',
                algorithm = 'XGBClassifier',
                data_dependent = 'scale_pos_weight')}
        return self

    def _draft_cluster(self) -> None:
        self.options = {
            'affinity': Outline(
                name = 'affinity',
                module = 'sklearn.cluster',
                algorithm = 'AffinityPropagation'),
            'agglomerative': Outline(
                name = 'agglomerative',
                module = 'sklearn.cluster',
                algorithm = 'AgglomerativeClustering'),
            'birch': Outline(
                name = 'birch',
                module = 'sklearn.cluster',
                algorithm = 'Birch'),
            'dbscan': Outline(
                name = 'dbscan',
                module = 'sklearn.cluster',
                algorithm = 'DBSCAN'),
            'kmeans': Outline(
                name = 'kmeans',
                module = 'sklearn.cluster',
                algorithm = 'KMeans'),
            'mean_shift': Outline(
                name = 'mean_shift',
                module = 'sklearn.cluster',
                algorithm = 'MeanShift'),
            'spectral': Outline(
                name = 'spectral',
                module = 'sklearn.cluster',
                algorithm = 'SpectralClustering'),
            'svm_linear': Outline(
                name = 'svm_linear',
                module = 'sklearn.cluster',
                algorithm = 'OneClassSVM'),
            'svm_poly': Outline(
                name = 'svm_poly',
                module = 'sklearn.cluster',
                algorithm = 'OneClassSVM'),
            'svm_rbf': Outline(
                name = 'svm_rbf',
                module = 'sklearn.cluster',
                algorithm = 'OneClassSVM,'),
            'svm_sigmoid': Outline(
                name = 'svm_sigmoid',
                module = 'sklearn.cluster',
                algorithm = 'OneClassSVM')}
        return self

    def _draft_regress(self) -> None:
        self.options = {
            'adaboost': Outline(
                name = 'adaboost',
                module = 'sklearn.ensemble',
                algorithm = 'AdaBoostRegressor'),
            'baseline_regressor': Outline(
                name = 'baseline_regressor',
                module = 'sklearn.dummy',
                algorithm = 'DummyRegressor',
                required = {'strategy': 'mean'}),
            'bayes_ridge': Outline(
                name = 'bayes_ridge',
                module = 'sklearn.linear_model',
                algorithm = 'BayesianRidge'),
            'lasso': Outline(
                name = 'lasso',
                module = 'sklearn.linear_model',
                algorithm = 'Lasso'),
            'lasso_lars': Outline(
                name = 'lasso_lars',
                module = 'sklearn.linear_model',
                algorithm = 'LassoLars'),
            'ols': Outline(
                name = 'ols',
                module = 'sklearn.linear_model',
                algorithm = 'LinearRegression'),
            'random_forest': Outline(
                name = 'random_forest',
                module = 'sklearn.ensemble',
                algorithm = 'RandomForestRegressor'),
            'ridge': Outline(
                name = 'ridge',
                module = 'sklearn.linear_model',
                algorithm = 'Ridge'),
            'svm_linear': Outline(
                name = 'svm_linear',
                module = 'sklearn.svm',
                algorithm = 'SVC',
                required = {'kernel': 'linear', 'probability': True}),
            'svm_poly': Outline(
                name = 'svm_poly',
                module = 'sklearn.svm',
                algorithm = 'SVC',
                required = {'kernel': 'poly', 'probability': True}),
            'svm_rbf': Outline(
                name = 'svm_rbf',
                module = 'sklearn.svm',
                algorithm = 'SVC',
                required = {'kernel': 'rbf', 'probability': True}),
            'svm_sigmoid': Outline(
                name = 'svm_sigmoid ',
                module = 'sklearn.svm',
                algorithm = 'SVC',
                required = {'kernel': 'sigmoid', 'probability': True}),
            'xgboost': Outline(
                name = 'xgboost',
                module = 'xgboost',
                algorithm = 'XGBRegressor',
                data_dependent = 'scale_pos_weight')}
        return self

    def _get_conditional(self,
            step: str,
            parameters: Dict[str, Any]) -> None:

        if step in ['xgboost'] and self.gpu:
            parameters.update({'tree_method': 'gpu_exact'})
        elif step in ['tensorflow']:
            algorithm = create_tensorflow_model(
                step = step,
                parameters = parameters)
        return parameters

    """ Core siMpLify Methods """

    def draft(self) -> None:
        super().draft()
        getattr(self, ''.join(['_draft_', self.model_type]))()
        if self.gpu:
            getattr(self, ''.join('_add_gpu_steps_', self.model_type))()
        return self


def create_tensorflow_model(step: 'Page', parameters: dict) -> None:
    algorithm = None
    return algorithm


#    def _downcast_features(self, ingredients):
#        dataframes = ['x_train', 'x_test']
#        number_types = ['uint', 'int', 'float']
#        feature_bits = ['64', '32', '16']
#        for df in dataframes:
#            for column in df.columns.keys():
#                if (column in ingredients.floats
#                        or column in ingredients.integers):
#                    for number_type in number_types:
#                        for feature_bit in feature_bits:
#                            try:
#                                df[column] = df[column].astype()

#
#    def _set_feature_types(self):
#        self.type_interface = {'boolean': tensorflow.bool,
#                               'float': tensorflow.float16,
#                               'integer': tensorflow.int8,
#                               'string': object,
#                               'categorical': CategoricalDtype,
#                               'list': list,
#                               'datetime': datetime64,
#                               'timedelta': timedelta}


#    def _tensor_flow_model(self):
#        from keras.models import Sequential
#        from keras.layers import Dense, Dropout, Activation, Flatten
#        classifier = Sequential()
#        classifier.add(Dense(units = 6, kernel_initializer = 'uniform',
#            activation = 'relu', input_dim = 30))
#        classifier.add(Dense(units = 6, kernel_initializer = 'uniform',
#            activation = 'relu'))
#        classifier.add(Dense(units = 1, kernel_initializer = 'uniform',
#            activation = 'sigmoid'))
#        classifier.compile(optimizer = 'adam',
#                           loss = 'binary_crossentropy',
#                           metrics = ['accuracy'])
#        return classifier
#        model = Sequential()
#        model.add(Activation('relu'))
#        model.add(Activation('relu'))
#        model.add(Dropout(0.25))
#        model.add(Flatten())
#        for layer_size in self.parameters['dense_layer_sizes']:
#            model.add(Dense(layer_size))
#            model.add(Activation('relu'))
#        model.add(Dropout(0.5))
#        model.add(Dense(2))
#        model.add(Activation('softmax'))
#        model.compile(loss = 'categorical_crossentropy',
#                      optimizer = 'adadelta',
#                      metrics = ['accuracy'])
#        return model



def create_torch_model(step: 'Page', parameters: dict) -> None:
    algorithm = None
    return algorithm


def create_stan_model(step: 'Page', parameters: dict) -> None:
    algorithm = None
    return algorithm

