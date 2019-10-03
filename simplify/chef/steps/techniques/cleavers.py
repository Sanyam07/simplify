"""
.. module:: cleavers
:synopsis: algorithms for cleaving features
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

from simplify.core.technique import SimpleTechnique


@dataclass
class CompareCleaves(SimpleTechnique):
    """Creates groups of features for comparison.

    The particular method applied is chosen between 'box-cox' and 'yeo-johnson'
    based on whether the particular data column has values below zero.

    Args:
        technique(str): name of technique used.
        parameters(dict): dictionary of parameters to pass to selected
            algorithm.
        name(str): name of class for matching settings in the Idea instance
            and for labeling the columns in files exported by Critic.
        auto_publish(bool): whether 'fina
        lize' method should be called when
            the class is instanced. This should generally be set to True.
    """

    technique: object = None
    parameters: object = None
    name: str = 'comparison_cleaver'
    auto_publish: bool = True

    def __post_init__(self):
        super().__post_init__()
        return self


@dataclass
class CombineCleaves(SimpleTechnique):
    """Creates groups of features for interaction.

    The particular method applied is chosen between 'box-cox' and 'yeo-johnson'
    based on whether the particular data column has values below zero.

    Args:
        technique(str): name of technique used.
        parameters(dict): dictionary of parameters to pass to selected
            algorithm.
        name(str): name of class for matching settings in the Idea instance
            and for labeling the columns in files exported by Critic.
        auto_publish(bool): whether 'fina
        lize' method should be called when
            the class is instanced. This should generally be set to True.
    """

    technique: object = None
    parameters: object = None
    name: str = 'combiner_cleaver'
    auto_publish: bool = True

    def __post_init__(self):
        super().__post_init__()
        return self


@dataclass
class SumFeatures(SimpleTechnique):
    """Creates feature interactions using addition.

    The particular method applied is chosen between 'box-cox' and 'yeo-johnson'
    based on whether the particular data column has values below zero.

    Args:
        technique(str): name of technique used.
        parameters(dict): dictionary of parameters to pass to selected
            algorithm.
        name(str): name of class for matching settings in the Idea instance
            and for labeling the columns in files exported by Critic.
        auto_publish(bool): whether 'fina
        lize' method should be called when
            the class is instanced. This should generally be set to True.
    """

    technique: object = None
    parameters: object = None
    name: str = 'gaussifier'
    auto_publish: bool = True

    def __post_init__(self):
        super().__post_init__()
        return self