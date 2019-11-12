"""
.. module:: ledger
:synopsis: data explorer and summarizer
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import pandas as pd

from simplify.core.base import SimpleComposite
from simplify.core.decorators import numpy_shield
from simplify.core.plan import SimplePlan
from simplify.core.planner import SimplePlanner
from simplify.core.technique import SimpleComposer


@dataclass
class Ledger(SimplePlanner):
    """

    Args:


    """
    name: Optional[str] = 'actuary'
    techniques: Optional[Dict[str, SimpleComposite]] = None

    def __post_init__(self) -> None:
        super().__post_init__()
        return self

    """ Private Methods """

    def _implement(self, recipe = None, transpose = True,
                  file_name = 'data_report', file_format = 'csv'):
        """Creates a DataFrame of common report data.

        Args:
            df(DataFrame): data to create report report for.
            transpose(bool): whether the 'df' columns should be listed
                horizontally (True) or vertically (False) in 'report'.
            file_name(str): name of file to be exported (without extension).
            file_format(str): exported file format.
        """
        self._implement_report(df = recipe.ingredients.df)
        self._implement_export_parameters(file_name = file_name,
                                          file_format = file_format,
                                          transpose = transpose)
        return self

    def _implement_export_parameters(self, file_name, file_format, transpose):
        self.export_parameters = {
            'folder': 'experiment',
            'file_name': file_name,
            'file_format': file_format}
        if not transpose:
            self.report = self.report.transpose()
            self.export_parameters.update({'header': False, 'index': True})
        else:
            self.export_parameters.update({'header': True, 'index': False})
        return self

    def _implement_report(self, df):
        for column in df.columns:
            row = pd.Series(index = self.columns)
            row['variable'] = column
            if df[column].dtype == bool:
                df[column] = df[column].astype(int)
            if df[column].dtype.kind in 'bifcu':
                for key, value in self.options.items():
                    if isinstance(value, str):
                        row[key] = getattr(df[column], value)()
                    elif isinstance(value, list):
                        if len(value) < 2:
                            row[key] = getattr(df[column], value[0])
                        elif isinstance(value[1], list):
                            row[key] = getattr(df[column],
                               value[0])()[value[1]]
                        else:
                            row[key] = getattr(df[column],
                               value[0])(value[1])
            self.report.loc[len(self.report)] = row
        return self

    def _start_report(self):
        self.columns = ['variable'] + (list(self.options.keys()))
        self.report = pd.DataFrame(columns = self.columns)
        return self
    
    """ Core siMpLify methods """

    def draft(self) -> None:
        """Sets default options for the Actuary's analysis."""
        options = {
            'summary': ('simplify.actuary.steps.summarize', 'Summarize'),
            'test': ('simplify.actuary.steps.test', 'Test')}
        self.options = SimpleOptions(options = options, parent = self)
        # Sets plan container
        self.plan_container = SimplePlan
        return self

    def publish(self, ingredients: ['Ingredients']) -> None:
        """
        """
        super().publish(ingredients = ingredients)
        return self