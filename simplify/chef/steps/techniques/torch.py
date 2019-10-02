"""
.. module:: torch
:synopsis: adapter for torch algorithms
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

from simplify.core.base import SimpleTechnique


@dataclass
class TorchModel(SimpleTechnique):
    """Applies Torch to data.

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
    auto_publish: bool = True
    name: str = 'torch'

    def __post_init__(self):
        super().__post_init__()
        return self

    def draft(self):
        super().draft()
        return self
