"""
.. module:: explain
:synopsis: explains machine learning results
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass, field
from typing import Dict

import numpy as np

from simplify.critic.collection import CriticTechnique


"""DEFAULT_OPTIONS are declared at the top of a module with a SimpleContributor
subclass because siMpLify uses a lazy importing system. This locates the
potential module importations in roughly the same place as normal module-level
import commands. A SimpleContributor subclass will, by default, add the
DEFAULT_OPTIONS to the subclass as the 'options' attribute. If a user wants
to use another set of 'options' for a subclass, they just need to pass
'options' when the class is instanced.
"""
DEFAULT_OPTIONS = {
    'eli5': ['simplify.critic.steps.steps.explainers', 'Eli5Explain'],
    'shap': ['simplify.critic.steps.steps.explainers', 'ShapExplain'],
    'skater': ['simplify.critic.steps.steps.explainers', 'SkaterExplain']}


@dataclass
class Explain(CriticTechnique):
    """Explains model results.

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
    name: str = 'explanations'
    auto_draft: bool = True
    lazy_import:bool = False
    options: Dict = field(default_factory = lambda: DEFAULT_OPTIONS)

    def __post_init__(self) -> None:
        super().__post_init__()
        return self

    """ Core siMpLify Methods """

    def draft(self) -> None:
        super().draft()
        return self