"""
.. module:: critic
:synopsis: model evaluation made simple
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass
from dataclasses import field
from typing import (Any, Callable, ClassVar, Dict, Iterable, List, Optional,
    Tuple, Union)

import pandas as pd

from simplify.core.book import Book
from simplify.core.book import Chapter
from simplify.core.repository import Repository
from simplify.core.repository import Plan
from simplify.core.technique import TechniqueOutline
from simplify.core.worker import Worker


@dataclass
class Anthology(Book):
    """Applies techniques to 'Cookbook' instances to assess performance.

    Args:
        name (Optional[str]): designates the name of the class used for internal
            referencing throughout siMpLify. If the class needs settings from
            the shared Idea instance, 'name' should match the appropriate
            section name in Idea. When subclassing, it is a good idea to use
            the same 'name' attribute as the base class for effective
            coordination between siMpLify classes. 'name' is used instead of
            __class__.__name__ to make such subclassing easier. Defaults to
            'critic'.
        iterable(Optional[str]): name of attribute for storing the main class
            instance iterable (called by __iter___). Defaults to 'reviews'.
        chapters (Optional['Plan']): iterable collection of steps and
            techniques to apply at each step. Defaults to an empty 'Plan'
            instance.

    """
    name: Optional[str] = field(default_factory = lambda: 'critic')
    iterable: Optional[str] = field(default_factory = lambda: 'reviews')
    chapters: Optional[List['Chapter']] = field(default_factory = list)



@dataclass
class Critic(Worker):
    """Applies an 'Anthology' instance to an applied 'Cookbook'.

    Args:
        idea ('Idea'): an 'Idea' instance with project settings.

    """
    idea: 'Idea'

    """ Private Methods """

    def _iterate_chapter(self,
            chapter: 'Chapter',
            data: Union['Dataset']) -> 'Chapter':
        """Iterates a single chapter and applies 'techniques' to 'data'.

        Args:
            chapter ('Chapter'): instance with 'techniques' to apply to 'data'.
            data (Union['Dataset', 'Book']): object for 'chapter'
                'techniques' to be applied.

        Return:
            'Chapter': with any changes made. Modified 'data' is added to the
                'Chapter' instance with the attribute name matching the 'name'
                attribute of 'data'.

        """
        for step, techniques in chapter.techniques.items():
            data = self._iterate_techniques(
                    techniques = techniques,
                    data = data)
        setattr(chapter, 'data', data)
        return chapter


@dataclass
class Evaluators(Repository):
    """A dictonary of TechniqueOutline options for the Analyst subpackage.

    Args:
        contents (Optional[str, Any]): default stored dictionary. Defaults to
            an empty dictionary.
        wildcards (Optional[List[str]]): a list of corresponding properties
            which access sets of dictionary keys. If none is passed, the two
            included properties ('default' and 'all') are used.
        defaults (Optional[List[str]]): a list of keys in 'contents' which
            will be used to return items when 'default' is sought. If not
            passed, 'default' will be set to all keys.

    """
    contents: Optional[Dict[str, Any]] = field(default_factory = dict)
    wildcards: Optional[List[str]] = field(default_factory = list)
    defaults: Optional[List[str]] = field(default_factory = list)
    idea: 'Idea' = None

    """ Private Methods """

    def create(self) -> None:
        self.contents = {
            'explain': {
                'eli5': TechniqueOutline(
                    name = 'eli5_explain',
                    module = 'simplify.critic.algorithms',
                    algorithm = 'Eli5Explain'),
                'shap': TechniqueOutline(
                    name = 'shap_explain',
                    module = 'simplify.critic.algorithms',
                    algorithm = 'ShapExplain'),
                'skater': TechniqueOutline(
                    name = 'skater_explain',
                    module = 'skater',
                    algorithm = '')},
            'predict': {
                'gini': TechniqueOutline(
                    name = 'gini_predict',
                    module = None,
                    algorithm = 'predict'),
                'shap': TechniqueOutline(
                    name = 'shap_predict',
                    module = 'shap',
                    algorithm = '')},
            'estimate': {
                'gini': TechniqueOutline(
                    name = 'gini_probabilities',
                    module = None,
                    algorithm = 'predict_proba'),
                'log': TechniqueOutline(
                    name = 'gini_probabilities',
                    module = None,
                    algorithm = 'predict_log_proba'),
                'shap': TechniqueOutline(
                    name = 'shap_probabilities',
                    module = 'shap',
                    algorithm = '')},
            'rank': {
                'permutation': TechniqueOutline(
                    name = 'permutation_importances',
                    module = None,
                    algorithm = ''),
                'gini': TechniqueOutline(
                    name = 'gini_importances',
                    module = None,
                    algorithm = 'feature_importances_'),
                'eli5': TechniqueOutline(
                    name = 'eli5_importances',
                    module = 'eli5',
                    algorithm = ''),
                'shap': TechniqueOutline(
                    name = 'shap_importances',
                    module = 'shap',
                    algorithm = '')},
            'measure': {
                'simplify': TechniqueOutline(
                    name = 'simplify_metrics',
                    module = 'simplify.critic.algorithms',
                    algorithm = 'compute_metrics'),
                'pandas': TechniqueOutline(
                    name = 'pandas_describe',
                    module = 'simplify.critic.algorithms',
                    algorithm = 'pandas_describe')},
            'report': {
                'simplify': TechniqueOutline(
                    name = 'simplify_report',
                    module = 'simplify.critic.algorithms',
                    algorithm = 'simplify_report'),
                'confusion': TechniqueOutline(
                    name = 'confusion_matrix',
                    module = 'sklearn.metrics',
                    algorithm = 'confusion_matrix'),
                'classification': TechniqueOutline(
                    name = 'classification_report',
                    module = 'sklearn.metrics',
                    algorithm = 'classification_report')}}
        return self
