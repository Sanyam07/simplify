"""
.. module:: divide
:synopsis: divides data source files into manageable sizes
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass
import os

from simplify.core.technique import SimpleTechnique


@dataclass
class Divide(SimpleTechnique):
    """Divides data source files so that they can be loaded in memory.

    Args:
        technique(str): name of technique.
        parameters(dict): dictionary of parameters to pass to selected
            algorithm.
        name(str): name of class for matching settings in the Idea instance
            and elsewhere in the siMpLify package.
        auto_publish(bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.
    """

    technique: object = None
    parameters: object = None
    name: str = 'converter'
    auto_publish: bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    def implement(self, ingredients):
        return self
