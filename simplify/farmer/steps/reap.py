
from dataclasses import dataclass
import os

from ...retool import ReTool
from ..harvest_step import HarvestStep


@dataclass
class Reap(HarvestStep):

    technique : str = ''
    parameters : object = None
    auto_prepare : bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    def _prepare_organize(self, key):
        file_path = os.path.join(self.inventory.instructions,
                                 'organizer_' + key + '.csv')
        self.parameters = {'technique' : self.technique,
                           'file_path' : file_path}
        algorithm = self.options[self.technique](**self.parameters)
        self._set_columns(algorithm)
        return algorithm

    def _prepare_parse(self, key):
        file_path = os.path.join(self.inventory.instructions,
                                 'parser_' + key + '.csv')
        self.parameters = {'technique' : self.technique,
                           'file_path' : file_path}
        algorithm = self.options[self.technique](**self.parameters)
        return algorithm

    def plan(self):
        self.options = {'organize' : ReTool,
                        'parse' : ReTool}
        return self

    def _set_columns(self, algorithm):
        prefix = algorithm.matcher.section_prefix
        if not hasattr(self, 'columns'):
            self.columns = []
        new_columns = list(algorithm.expressions.values())
        new_columns = [prefix + '_' + column for column in self.columns]
        self.columns.extend(new_columns)
        return self

    def _perform_organize(self, ingredients, algorithm):
        ingredients.df, ingredients.source = algorithm.perform(
                df = ingredients.df, source = ingredients.source)
        return ingredients

    def _perform_parse(self, ingredients, algorithm):
        ingredients.df = algorithm.perform(df = ingredients.df,
                                         source = ingredients.source)
        return ingredients

    def prepare(self):
        for key in self.parameters:
            if hasattr(self, '_prepare_' + self.technique):
                algorithm = getattr(
                        self, '_prepare_' + self.technique)(key = key)
            else:
                algorithm = getattr(self, '_prepare_generic_list')(key = key)
            self.algorithms.append(algorithm)
        return self