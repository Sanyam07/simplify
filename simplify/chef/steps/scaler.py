"""
.. module:: scaler
:synopsis: scales or bins numerical features
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

from simplify.chef.composer import ChefAlgorithm as Algorithm
from simplify.chef.composer import ChefComposer as Composer
from simplify.chef.composer import ChefTechnique as Technique


@dataclass
class Scaler(Composer):
    """Scales numerical data."""

    name: str = 'scaler'

    def __post_init__(self):
        self.idea_sections = ['chef']
        super().__post_init__()
        return self

    def draft(self):
        self.bins = Technique(
            name = 'bins',
            module = 'sklearn.preprocessing',
            algorithm = 'KBinsDiscretizer',
            default_parameters = {
                'encode': 'ordinal',
                'strategy': 'uniform',
                'n_bins': 5},
            selected_parameters = True)
        # self.gauss = Technique(
        #     name = 'gauss',
        #     module = None,
        #     algorithm = Gaussify,
        #     default_parameters = {'standardize': False, 'copy': False},
        #     extra_parameters = {'rescaler': self.standard},
        #     selected_parameters = True)
        self.maxabs = Technique(
            name = 'maxabs',
            module = 'sklearn.preprocessing',
            algorithm = 'MaxAbsScaler',
            default_parameters = {'copy': False},
            selected_parameters = True)
        self.minmax = Technique(
            name = 'minmax',
            module = 'sklearn.preprocessing',
            algorithm = 'MinMaxScaler',
            default_parameters = {'copy': False},
            selected_parameters = True)
        self.normalize = Technique(
            name = 'normalize',
            module = 'sklearn.preprocessing',
            algorithm = 'Normalizer',
            default_parameters = {'copy': False},
            selected_parameters = True)
        self.quantile = Technique(
            name = 'quantile',
            module = 'sklearn.preprocessing',
            algorithm = 'QuantileTransformer',
            default_parameters = {'copy': False},
            selected_parameters = True)
        self.robust = Technique(
            name = 'robust',
            module = 'sklearn.preprocessing',
            algorithm = 'RobustScaler',
            default_parameters = {'copy': False},
            selected_parameters = True)
        self.standard = Technique(
            name = 'standard',
            module = 'sklearn.preprocessing',
            algorithm = 'StandardScaler',
            default_parameters = {'copy': False},
            selected_parameters = True)
        super().draft()
        return self


# @dataclass
# class Gaussify(ChefAlgorithm):
#     """Transforms data columns to more gaussian distribution.

#     The particular method applied is chosen between 'box-cox' and 'yeo-johnson'
#     based on whether the particular data column has values below zero.

#     Args:
#         technique(str): name of technique used.
#         parameters(dict): dictionary of parameters to pass to selected
#             algorithm.
#         name(str): name of class for matching settings in the Idea instance
#             and for labeling the columns in files exported by Critic.
#         auto_draft(bool): whether 'finalize' method should be called when
#             the class is instanced. This should generally be set to True.
#     """

#     technique: str = 'box-cox and yeo-johnson'
#     parameters: object = None
#     name: str = 'gaussifier'

#     def __post_init__(self):
#         self.idea_sections = ['chef']
#         super().__post_init__()
#         return self

#     def draft(self):
#         self.rescaler = self.parameters['rescaler'](
#                 copy = self.parameters['copy'])
#         del self.parameters['rescaler']
#         self._publish_parameters()
#         self.positive_tool = self.options['box_cox'](
#                 method = 'box_cox', **self.parameters)
#         self.negative_tool = self.options['yeo_johnson'](
#                 method = 'yeo_johnson', **self.parameters)
#         return self

#     def publish(self, ingredients, columns = None):
#         if not columns:
#             columns = ingredients.numerics
#         for column in columns:
#             if ingredients.x[column].min() >= 0:
#                 ingredients.x[column] = self.positive_tool.fit_transform(
#                         ingredients.x[column])
#             else:
#                 ingredients.x[column] = self.negative_tool.fit_transform(
#                         ingredients.x[column])
#             ingredients.x[column] = self.rescaler.fit_transform(
#                     ingredients.x[column])
#         return ingredients
