
from dataclasses import dataclass
import pandas as pd
import re

from ..ingredients import Ingredients


@dataclass
class Blackacre(object):
    """Parent class for various classes in the siMpLify Almanac subpackage to
    allow sharing of methods.
    """
    def __post_init__(self):
        if self.auto_prepare:
            self.prepare()
        return self

    def _check_ingredients(self):
        if self.ingredients == None:
            self.ingredients = Ingredients(menu = self.menu,
                                           inventory = self.inventory)
        return self

    def _check_stages(self):
        if not self.stages:
            self.stages = self.menu['harvest']['harvest_stages']
        return self

    def _check_variable(self, variable):
        """Checks if variable exists as attribute in class."""
        if hasattr(self, variable):
            return variable
        else:
            error = self.__class__.__name__ + ' does not contain ' + variable
            raise KeyError(error)

    def _combine_lists(self, *args, **kwargs):
        """Combines lists to create a tuple."""
        return zip(*args, **kwargs)

    def _listify(self, variable):
        """Checks to see if the variable are stored in a list. If not, the
        variable is converted to a list or a list of 'none' is created.
        """
        if not variable:
            return ['none']
        elif isinstance(variable, list):
            return variable
        else:
            return [variable]

    def _list_to_string(self, variable):
        """Converts a list to a string with a comma and space separating each
        item. The conversion applies whether variable is a simple list or
        pandas series
        """
        if isinstance(variable, pd.Series):
            out_value = variable.apply(', '.join)
        elif isinstance(variable, list):
            out_value = ', '.join(variable)
        else:
            msg = 'Value must be a list or pandas series containing lists'
            raise TypeError(msg)
            out_value = variable
        return out_value

    def _no_breaks(self, variable, in_column = None):
        """Removes line breaks and replaces them with single spaces. Also,
        removes hyphens at the end of a line and connects the surrounding text.
        Takes either string, pandas series, or pandas dataframe as input and
        returns the same.
        """
        if isinstance(variable, pd.DataFrame):
            variable[in_column].str.replace('[a-z]-\n', '')
            variable[in_column].str.replace('\n', ' ')
        elif isinstance(variable, pd.Series):
            variable.str.replace('[a-z]-\n', '')
            variable.str.replace('\n', ' ')
        else:
            variable = re.sub('[a-z]-\n', '', variable)
            variable = re.sub('\n', ' ', variable)
        return variable

    def _no_double_space(self, variable, in_column = None):
        """Removes double spaces and replaces them with single spaces from a
        string. Takes either string, pandas series, or pandas dataframe as
        input and returns the same.
        """
        if isinstance(variable, pd.DataFrame):
            variable[in_column].str.replace('  +', ' ')
        elif isinstance(variable, pd.Series):
            variable.str.replace('  +', ' ')
        else:
            variable = variable.replace('  +', ' ')
        return variable

    def _remove_excess(self, variable, excess, in_column = None):
        """Removes excess text included when parsing text into sections and
        strips text. Takes either string, pandas series, or pandas dataframe as
        input and returns the same.
        """
        if isinstance(variable, pd.DataFrame):
            variable[in_column].str.replace(excess, '')
            variable[in_column].str.strip()
        elif isinstance(variable, pd.Series):
            variable.str.replace(excess, '')
            variable.str.strip()
        else:
            variable = re.sub(excess, '', variable)
            variable = variable.strip()
        return variable

    def _word_count(self, variable):
        """Returns word court for a string."""
        return len(variable.split(' ')) - 1