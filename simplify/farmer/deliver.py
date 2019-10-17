"""
.. module:: deliver
:synopsis: completes data gathering and preparation process
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

import pandas as pd

from simplify.core.technique import FarmerTechnique


"""DEFAULT_OPTIONS are declared at the top of a module with a SimpleClass
subclass because siMpLify uses a lazy importing system. This locates the
potential module importations in roughly the same place as normal module-level
import commands. A SimpleClass subclass will, by default, add the
DEFAULT_OPTIONS to the subclass as the 'options' attribute. If a user wants
to use another set of 'options' for a subclass, they just need to pass
'options' when the class is instanced.
"""
DEFAULT_OPTIONS = {
    'reshape': ['simplify.farmer.steps.reshape', 'Reshape'],
    'streamline': ['simplify.farmer.steps.streamline', 'Streamline']}


@dataclass
class Deliver(SimpleIterable):
    """Makes final structural changes to data before analysis.

    Args:
        steps(dict): dictionary containing keys of FarmerTechnique names (strings)
            and values of FarmerTechnique class instances.
        name(str): name of class for matching settings in the Idea instance
            and elsewhere in the siMpLify package.
        auto_publish(bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.
    """

    steps: object = None
    name: str = 'delivery'
    auto_publish: bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    def _publish_shapers(self, harvest):
        self.algorithm = self.options[self.technique](**self.parameters)
        return self

    def _publish_streamliners(self, harvest):
        self.algorithm = self.options[self.technique](**self.parameters)
        return self

    def draft(self):
        self.needed_parameters = {'shapers': ['shape_type', 'stubs',
                                               'id_column', 'values',
                                               'separator'],
                                  'streamliners': ['method']}
        return self

    def implement(self, ingredients):
        ingredients = self.algorithm.implement(ingredients)
        return ingredients
