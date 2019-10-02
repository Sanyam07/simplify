"""
.. module:: supplement
:synopsis: adds new data to existing DataFrame
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

from simplify.core.base import SimpleStep


@dataclass
class Supplement(SimpleStep):
    """Adds new data to similarly structured DataFrame.

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
    name: str = 'supplementer'
    auto_publish: bool = True

    def __post_init__(self):
        return self

    def draft(self):
        self.options = {}
        return self

    def produce(self, ingredients, sources):
        return ingredients