
from dataclasses import dataclass
import os

import numpy as np

from ...implements import ReFrame
from ...managers import Step, Technique


@dataclass
class Clean(Step):

    technique : str = ''
    parameters : object = None
    auto_prepare : bool = True
    name : str = 'cleaner'

    def __post_init__(self):
        super().__post_init__()
        return self

    def _prepare_combiners(self, almanac):
        for key, value in almanac.combiners.items():
            source_column = 'section_' + key
            out_column = key
            mapper = 'any'
            self.techniques.update({key : self.options['combiners'](
                    source_column = source_column,
                    out_column = out_column,
                    mapper = mapper)})
        return self

    def _prepare_parsers(self, almanac):
        for key, value in almanac.parsers.items():
            file_path = os.path.join(self.inventory.parsers, key +  '.csv')
            out_prefix = key + '_'
            self.techniques.update(
                    {'parsers' :  {'file_path' : file_path,
                                   'compile_keys' : True,
                                   'out_prefix' : out_prefix}})
        return self

    def _set_defaults(self):
        self.options = {'parsers' : ReFrame,
                        'combiners' : Combine}
        return self

    def start(self, ingredients, almanac):
        ingredients.df = self.technique.match(ingredients.df)
        return ingredients

@dataclass
class Combine(Technique):

    source_column : str = ''
    out_column : str = ''
    mapper : object = None

    def __post_init__(self):
        return self

    def _combine_list_all(self, df, in_columns, out_column):
        df[out_column] = np.where(np.all(df[self._listify(in_columns)]),
                                         True, False)
        return self

    def _combine_list_any(self, df, in_columns, out_column):
        df[out_column] = np.where(np.any(df[self._listify(in_columns)]),
                                         True, False)
        return self

    def _combine_list_dict(self, df, in_columns, out_column, combiner):
        df[out_column] = np.where(np.any(
                                df[self._listify(in_columns)]),
                                True, False)

    def start(self, ingredients):
        return ingredients