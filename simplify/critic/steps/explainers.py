"""
.. module:: explainers
:synopsis: tools for explaining machine learning results
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass, field
from typing import Dict

import numpy as np

from simplify.critic.collection import CriticTechnique


@dataclass
class Eli5Explain(CriticTechnique):
    """Explains fit model with eli5 package.

    Args:
        step(str): name of step.
        parameters(dict): dictionary of parameters to pass to selected
            algorithm.
        name(str): designates the name of the class which is used throughout
            siMpLify to match methods and settings with this class and
            identically named subclasses.
        auto_draft(bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.

    """

    step: object = None
    parameters: object = None
    name: str = 'eli5'
    auto_draft: bool = True
    options: Dict = field(default_factory = lambda: ELI5_DEFAULT_OPTIONS)

    def __post_init__(self) -> None:
        super().__post_init__()
        return self

    """ Core siMpLify Methods """

    def draft(self) -> None:
        super().draft()
        self.models = {
            'baseline': 'none',
            'catboost': 'specific',
            'decision_tree': 'specific',
            'lasso': 'specific',
            'lasso_lars': 'specific',
            'light_gbm': 'specific',
            'logit': 'specific',
            'ols': 'specific',
            'random_forest': 'specific',
            'ridge': 'specific',
            'svm_linear': 'specific',
            'tensor_flow': 'permutation',
            'torch': 'permutation',
            'xgboost': 'specific'}
        return self

    def publish(self, recipe):
        base_score, score_decreases = get_score_importances(score_func, X, y)
        feature_importances = np.mean(score_decreases, axis=0)
        from eli5 import show_weights
        self.permutation_weights = show_weights(
                self.permutation_importances,
                feature_names = recipe.ingredients.columns.keys())
        return self


@dataclass
class ShapExplain(CriticTechnique):
    """Explains fit model with shap package.

    Args:
        step(str): name of step.
        parameters(dict): dictionary of parameters to pass to selected
            algorithm.
        name(str): designates the name of the class which is used throughout
            siMpLify to match methods and settings with this class and
            identically named subclasses.
        auto_draft(bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.

    """

    step: object = None
    parameters: object = None
    name: str = 'shap_explanation'
    auto_draft: bool = True
    options: Dict = field(default_factory = lambda: SHAP_DEFAULT_OPTIONS)

    def __post_init__(self) -> None:
        super().__post_init__()
        return self

    """ Private Methods """

    def _set_method(self, recipe):
        if self.step in self.models:
            self.method = self.library[self.models[self.step]]
        else:
            self.method = self.library['kernel']
        self.evaluator = self.method(
            model = recipe.model.algorithm,
            data = getattr(recipe.ingredients, 'x_' + self.data_to_review))
        return self

    """ Core siMpLify Methods """

    def draft(self) -> None:
        self.models = {
            'baseline': 'none',
            'catboost': 'tree',
            'decision_tree': 'tree',
            'lasso': 'linear',
            'lasso_lars': 'linear',
            'light_gbm': 'tree',
            'logit': 'linear',
            'ols': 'linear',
            'random_forest': 'tree',
            'ridge': 'linear',
            'svm_linear': 'linear',
            'tensor_flow': 'deep',
            'torch': 'deep',
            'xgboost': 'tree'}
        return self

    def publish(self, recipe):
        """Applies shap evaluator to data based upon type of model used."""
        if self.step != 'none':
            self._set_method()
            setattr(recipe, self.name + '_values', self.evaluator.shap_values(
                    getattr(recipe.ingredients, 'x_' + self.data_to_review)))
            if not hasattr(recipe, self.name):
                setattr(recipe, self.name, [])
            getattr(recipe, self.name).append(self.name)
            if self.method == 'tree':
                setattr(recipe, self.name + '_interactions',
                        self.evaluator.shap_interaction_values(
                                getattr(recipe.ingredients,
                                        'x_' + self.data_to_review)))
            getattr(recipe, self.name).append(
                    getattr(self, self.name + '_interactions'))
        return getattr(recipe, self.name)


@dataclass
class SkaterExplain(CriticTechnique):
    """Explains fit model with skater package.

    Args:
        step(str): name of step.
        parameters(dict): dictionary of parameters to pass to selected
            algorithm.
        name(str): designates the name of the class which is used throughout
            siMpLify to match methods and settings with this class and
            identically named subclasses.
        auto_draft(bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.

    """

    step: object = None
    parameters: object = None
    name: str = 'skater'
    auto_draft: bool = True
    options: Dict = field(default_factory = lambda: SKATER_DEFAULT_OPTIONS)

    def __post_init__(self) -> None:
        super().__post_init__()
        return self

    def draft(self) -> None:
        return self
