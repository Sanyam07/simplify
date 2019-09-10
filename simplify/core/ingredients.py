
from dataclasses import dataclass
from functools import wraps
from inspect import getfullargspec
import os

import numpy as np
import pandas as pd

from .summary import Summary
from .types import DataTypes


@dataclass
class Ingredients(object):
    """Imports, stores, and exports pandas DataFrames and Series, as well as
    related information about those data containers.

    Ingredients uses pandas DataFrames or Series for all data storage, but it
    utilizes faster numpy methods where possible to increase performance.
    Ingredients stores the data itself as well as related variables containing
    information about the data.

    DataFrames stored in ingredients can be imported and exported using the
    load and save methods from the Inventory class.

    Ingredients adds easy-to-use methods for common feature engineering
    techniques. In addition, any user function can be applied to a DataFrame
    or Series contained in Ingredients by using the apply method.

    Parameters:

        menu: an instance of Menu.
        inventory: an instance of Inventory.
        df: a pandas DataFrame or Series. This argument should be passed if
            the user has a pre-existing dataset.
        auto_prepare: a boolean variable indicating whether prepare method
            should be called when the class is instanced.
        default_df: a string listing the current default DataFrame or Series
            attribute that will be used when a specific DataFrame is not passed
            to a method. The default value is initially set to 'df'. The
            imported decorator check_df will look to the default_df to pick
            the appropriate DataFrame in such situations.
        x, y, x_train, y_train, x_test, y_test, x_val, y_val: DataFrames or
            Series. These DataFrames and Series need not be passed when the
            class is instanced. They are merely listed for users who already
            have divided datasets and still wish to use the siMpLify package.
        datatypes: dictionary containing column names and datatypes for
            DataFrames or Series.
        prefixes: dictionary containing list of prefixes for columns and
            corresponding datatypes for default DataFrame.
    """
    menu : object
    inventory : object
    df : object = None
    auto_prepare : bool = True
    auto_load : bool = False
    default_df : str = 'df'
    x : object = None
    y : object = None
    x_train : object = None
    y_train : object = None
    x_test : object = None
    y_test : object = None
    x_val : object = None
    y_val : object = None
    datatypes : object = None
    prefixes : object = None

    def __post_init__(self):
        # Creates menu attribute if string passed to menu when the class was
        # instanced and injects local attributes from menu configuration.
        self._check_menu()
        # Calls _outline private method to set up class defaults.
        self._outline()
        return self

    def __getattr__(self, attr):
        """Returns values from column datatypes, column datatype dictionary,
        and section prefixes dictionary.
        """
        if attr in ['x', 'y', 'x_train', 'y_train', 'x_test', 'y_test']:
            return self.__dict__[self.options[attr]]
        elif attr in ['booleans', 'floats', 'integers', 'strings',
                      'categoricals', 'lists', 'datetimes', 'timedeltas']:
            return self._get_columns_by_type(attr[:-1])
        elif (attr in ['scalers', 'encoders', 'mixers']
              and attr not in self.__dict__):
            return getattr(self, '_get_default_' + attr)()
        elif attr in ['columns']:
            if not self.datatypes:
                self.datatypes = {}
            return self.datatypes
        elif attr in ['sections']:
            if not self.prefixes:
                self.prefixes = {}
            return self.prefixes
        elif attr in self.__dict__:
            return self.__dict__[attr]
        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError
        else:
            return None

    def __setattr__(self, attr, value):
        """Sets values in column datatypes, column datatype dictionary, and
        section prefixes dictionary.
        """
        if attr in ['booleans', 'floats', 'integers', 'strings',
                    'categoricals', 'lists', 'datetimes', 'timedeltas']:
            self.__dict__['datatypes'].update(
                    dict.fromkeys(self.listify(
                            self._all_datatypes[attr[:-1]]), value))
            return self
        elif attr in ['columns']:
            self.__dict__['datatypes'].update({attr: value})
            return self
        elif attr in ['sections']:
            if not self.prefixes:
                self.__dict__['prefixes'] = {attr : value}
            else:
                self.__dict__['prefixes'].update({attr : value})
            return self
        else:
            self.__dict__[attr] = value
            return self

    def check_df(method):
        """Decorator which automatically uses the default DataFrame if one
        is not passed to the decorated method.

        Parameters:
            method: wrapped method.
        """
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            argspec = getfullargspec(method)
            unpassed_args = argspec.args[len(args):]
            if 'df' in argspec.args and 'df' in unpassed_args:
                kwargs.update({'df' : getattr(self, self.default_df)})
            return method(self, *args, **kwargs)
        return wrapper

    def column_list(method):
        """Decorator which creates a complete column list from kwargs passed
        to wrapped method.

        Parameters:
            method: wrapped method.
        """
        arguments_to_check = ['columns', 'prefixes', 'mask']
        new_kwargs = {}
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            argspec = getfullargspec(method)
            unpassed_args = argspec.args[len(args):]
            if ('columns' in unpassed_args
                    and 'prefixes' in unpassed_args
                    and 'mask' in unpassed_args):
                columns = list(self.datatypes.keys())
            else:
                for argument in arguments_to_check:
                    if argument in kwargs:
                        new_kwargs[argument] = kwargs[argument]
                    else:
                        new_kwargs[argument] = None
                    if argument in ['prefixes', 'mask'] and argument in kwargs:
                        del kwargs[argument]
                columns = self.create_column_list(**new_kwargs)
                kwargs.update({'columns' : columns})
            return method(self, **kwargs)
        return wrapper

    @property
    def full(self):
        """Returns the full dataset divided into x and y twice."""
        return (self.options['x'], self.options['y'],
                self.options['x'], self.options['y'])

    @property
    def test(self):
        """Returns the test data."""
        return self.options['x_test'], self.options['y_test']

    @property
    def train(self):
        """Returns the training data."""
        return self.options['x_train'], self.options['y_train']

    @property
    def train_test(self):
        """Returns the training and testing data."""
        return (*self.train, *self.test)

    @property
    def train_test_val(self):
        """Returns the training, test, and validation data."""
        return (*self.train, *self.test, *self.val)

    @property
    def train_val(self):
        """Returns the training and validation data."""
        return (*self.train, *self.val)

    @property
    def val(self):
        """Returns the validation data."""
        return self.options['x_val'], self.options['y_val']

    @property
    def xy(self):
        """Returns the full dataset divided into x and y."""
        return self.options['x'], self.options['y']

    def _check_columns(self, columns = None):
        """Returns self.datatypes if columns doesn't exist.

        Parameters:
            columns: list of column names."""
        return columns or list(self.datatypes.keys())

    def _check_menu(self):
        """Loads menu from an .ini file if a string is passed to menu instead
        of a menu instance. Injects sections of menu to class instance
        using user settings stored in or default.
        """
        if isinstance(self.menu, str):
            # Menu imported within function to avoid circular dependency.
            from simplify.core.menu import Menu
            self.menu = Menu(file_path = self.menu)
        # Adds attributes to class from appropriate sections of the menu.
        sections = ['general']
        if hasattr(self, 'menu_sections') and self.menu_sections:
            if isinstance(self.menu_sections, str):
                sections.append(self.menu_sections)
            else:
                sections.extend(self.menu_sections)
        if (hasattr(self, 'name')
                and self.name in self.menu.configuration
                and not self.name in sections):
            sections.append(self.name)
        self.menu.inject(instance = self, sections = sections)
        return self

    @check_df
    def _crosscheck_columns(self, df = None):
        """Removes any columns in datatypes dictionary, but not in df."""
        for column, datatype in self.datatypes.items():
            if column not in df.columns:
                del self.datatypes[column]
        return self

    def _get_columns_by_type(self, datatype):
        """Returns list of columns of the specified datatype.

        Parameters:
            datatype: string matching datatype in self.extensions.
        """
        return [k for k, v in self.datatypes.items() if v == datatype]

    def _get_default_encoders(self):
        return self.categoricals

    def _get_default_mixers(self):
        return []

    def _get_default_scalers(self):
        return self.integers + self.floats

    def _initialize_datatypes(self, df = None):
        """Initializes datatypes for columns of pandas DataFrame or Series if
        not already provided.
        """
        check_order = [df, getattr(self, self.default_df), self.x,
                       self.x_train]
        for _data in check_order:
            if isinstance(_data, pd.DataFrame) or isinstance(_data, pd.Series):
                if not self.datatypes:
                    self.infer_datatypes(df = _data)
                else:
                    self._crosscheck_columns(df = _data)
                break
        return self

    def _outline(self):
        """Sets defaults for Ingredients when class is instanced."""
        # Declares dictionary of DataFrames contained in Ingredients to allow
        # temporary remapping of attributes in __getattr__.
        self.default_options = {'x' : 'x',
                                'y' : 'y',
                                'x_train' : 'x_train',
                                'y_train' : 'y_train',
                                'x_test' : 'x_test',
                                'y_test' : 'y_test',
                                'x_val' : 'x_val',
                                'y_val' : 'y_val'}
        self.all_datatypes = DataTypes()
        if not self.datatypes:
            self.datatypes = {}
        if not self.sections:
            self.sections = {}
        # Maps class properties to appropriate DataFrames using the default
        # train_test setting.
        self._remap_dataframes(data_to_use = 'train_test')
        return self

    def _remap_dataframes(self, data_to_use = None):
        """Remaps DataFrames returned by various properties of Ingredients so
        that methods and classes of siMpLify can use the same labels for
        analyzing the Ingredients DataFrames.

        Parameters:
            data_to_use: a string corresponding to a class property indicating
                which set of data is to be returned when the corresponding
                property is called.
        """
        if not data_to_use:
            data_to_use = 'train_test'
        # Sets values in self.options which contains the mapping for class
        # attributes and DataFrames as determined in __getattr__.
        if data_to_use == 'train_test':
            self.options = self.default_options.copy()
        elif data_to_use == 'train_val':
            self.options['x_test'] = 'x_val'
            self.options['y_test'] = 'y_val'
        elif data_to_use == 'full':
            self.options['x_train'] = 'x'
            self.options['y_train'] = 'y'
            self.options['x_test'] = 'x'
            self.options['y_test'] = 'y'
        elif data_to_use == 'train':
            self.options['x'] = 'x_train'
            self.options['y'] = 'y_train'
        elif data_to_use == 'test':
            self.options['x'] = 'x_test'
            self.options['y'] = 'y_test'
        elif data_to_use == 'val':
            self.options['x'] = 'x_val'
            self.options['y'] = 'y_val'
        return self

    @check_df
    def add_unique_index(self, df = None, column = 'index_universal',
                         make_index = False):
        """Creates a unique integer index for each row.

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            column: string containing the column name for the index.
            make_index: boolean value indicating whether the index column
                should be made the index of the DataFrame."""
        if isinstance(df, pd.DataFrame):
            df[column] = range(1, len(df.index) + 1)
            self.datatypes.update({column, int})
            if make_index:
                df.set_index(column, inplace = True)
        else:
            error = 'To add an index, df must be a pandas DataFrame.'
            TypeError(error)
        return self

    @check_df
    def apply(self, df = None, func = None, **kwargs):
        """Allows users to pass a function to Ingredients instance which will
        be applied to the passed DataFrame (or uses default_df if none is
        passed).

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            func: function to be applied to the DataFrame.
            **kwargs: any arguments to be passed to func.
        """
        df = func(df, **kwargs)
        return self

    @column_list
    @check_df
    def auto_categorize(self, df = None, columns = None, threshold = 10):
        """Automatically assesses each column to determine if it has less than
        threshold unique values and is not boolean. If so, that column is
        converted to category type.

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            columns: a list of column names.
            threshold: integer of unique values necessary to form a category.
                If there are less unique values than the threshold, the column
                is converted to a category type. Otherwise, it will remain its
                current datatype.
        """
        for column in self._check_columns(columns):
            if column in df.columns:
                if not column in self.booleans:
                    if df[column].nunique() < threshold:
                        df[column] = df[column].astype('category')
            else:
                error = column + ' is not in ingredients DataFrame'
                raise KeyError(error)
        return self

    @column_list
    @check_df
    def change_datatype(self, df = None, columns = None, datatype = str):
        """Changes column datatypes of columns passed or columns with the
        prefixes passed. datatype becomes the new datatype for the columns.

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            columns: a list of column names.
            prefixes: a list of prefix names.
            datatype: a string containing the datatype to convert the columns
                and columns with prefixes to.
        """
        for column in columns:
            self.datatypes[column] = datatype
        self.convert_column_datatypes(df = df)
        return self

    @check_df
    def conform(self, df = None, step = None):
        """Adjusts some of the siMpLify-specific datatypes to the appropriate
        datatype based upon the current step.

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            step: string corresponding to the current state.
        """
        self.step = step
        for column, datatype in self.datatypes.items():
            if self.step in ['harvest', 'clean']:
                if datatype in ['category', 'encoder', 'interactor']:
                    self.datatypes[column] = str
            elif self.step in ['bundle', 'deliver']:
                if datatype in ['list', 'pattern']:
                    self.datatypes[column] = 'category'
        self.convert_column_datatypes(df = df)
        return self

    @check_df
    def convert_column_datatypes(self, df = None, raise_errors = False):
        """Attempts to convert all column data to the datatypes in
        self.datatypes.

        Parameters:
            df: pandas DataFrame. If none is provided, the default DataFrame
                is used.
            raise_errors: a boolean variable indicating whether errors should
                be raised when converting datatypes or ignored.
        """
        if raise_errors:
            raise_errors = 'raise'
        else:
            raise_errors = 'ignore'
        for column, datatype in self.datatypes.items():
            if not isinstance(datatype, str):
                df[column].astype(dtype = datatype,
                                  copy = False,
                                  errors = raise_errors)
        self.downcast(df = df)
        return self

    @column_list
    @check_df
    def convert_rare(self, df = None, columns = None, threshold = 0):
        """Converts categories rarely appearing within categorical columns
        to empty string if they appear below the passed threshold. threshold is
        defined as the percentage of total rows.

        Parameters:
            df: a pandas DataFrame.
            columns: a list of columns to check. If not passed, all columns
                in self.datatypes listed as 'categorical' type are used.
            threshold: a float indicating the percentage of values in rows
                below which a default_value is substituted.
        """
        if not columns:
            columns = self.categoricals
        for column in columns:
            if column in df.columns:
                df['value_freq'] = (
                        df[column].value_counts() / len(df[column]))
                df[column] = np.where(df['value_freq'] <= threshold,
                                      self.default_values['categorical'],
                                      df[column])
            else:
                error = column + ' is not in DataFrame'
                raise KeyError(error)
        if 'value_freq' in df.columns:
            df.drop('value_freq', axis = 'columns', inplace = True)
        return self

    @check_df
    def create_column_list(self, df = None, columns = None, prefixes = None,
                           mask = None):
        """Dynamically creates a new column list from a list of columns and/or
        lists of prefixes.

        Parameters:
            df: pandas DataFrame.
            columns: list of columns.
            prefixes: list of prefixes for columns.
            mask: numpy array, list, or pandas Series, of booleans of columns.
        """
        column_names = []
        if (isinstance(mask, np.ndarray)
                or isinstance(mask, list)
                or isinstance(mask, pd.Series)):
            for boolean, feature in zip(mask, list(df.columns)):
                if boolean:
                    column_names.append(feature)
        else:
            temp_list = []
            prefixes_list = []
            if prefixes:
                for prefix in self.listify(prefixes):
                    temp_list = [col for col in df if col.startswith(prefix)]
                    prefixes_list.extend(temp_list)
            if columns:
                if prefixes:
                    column_names = self.listify(columns) + prefixes_list
                else:
                    column_names = self.listify(columns)
            else:
                column_names = prefixes_list
        return column_names

    @column_list
    def create_series(self, columns = None, return_series = False):
        """Creates a Series (row) with the datatypes in columns.

        Parameters:
            columns: a list of index names for pandas series.
            return_series: boolean value indicating whether the Series should
                be returned (True) or assigned to attribute named in default_df
                (False):
        """
        # If columns is not passed, the keys of self.datatypes are used.
        if not columns and self.datatypes:
            columns = list(self.datatypes.keys())
        row = pd.Series(index = columns)
        # Fills series with default_values based on datatype.
        if self.datatypes:
            for column, datatype in self.datatypes.items():
                row[column] = self.default_values[datatype]
        if return_series:
            return row
        else:
            setattr(self, self.default_df, row)
            return self

    @column_list
    @check_df
    def decorrelate(self, df = None, columns = None, threshold = 0.95):
        """Drops all but one column from highly correlated groups of columns.
        threshold is based upon the .corr() method in pandas. columns can
        include any datatype accepted by .corr(). If columns is set to None,
        all columns in the DataFrame are tested.

        Parameters:
            df: a pandas DataFrame.
            threshold: a float indicating the level of correlation using
                pandas corr method above which a column is dropped.
        """
        if columns:
            corr_matrix = df[columns].corr().abs()
        else:
            corr_matrix = df.corr().abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape),
                                          k = 1).astype(np.bool))
        corrs = [col for col in upper.corrs if any(upper[col] > threshold)]
        self.drop_columns(columns = corrs)
        return self

    @column_list
    @check_df
    def downcast(self, df = None, columns = None):
        """Decreases memory usage by downcasting datatypes. For numerical
        datatypes, the method attempts to cast the data to unsigned integers if
        possible.

        Parameters:
            df: a pandas DataFrame.
            columns: a list of columns to downcast
        """
        for column in self._check_columns(columns):
            if column in df.columns:
                if self.datatypes[column] in ['boolean']:
                    df[column] = df[column].astype(bool)
                elif self.datatypes[column] in ['integer', 'float']:
                    try:
                        df[column] = pd.to_numeric(df[column],
                                                   downcast = 'integer')
                        if min(df[column] >= 0):
                            df[column] = pd.to_numeric(df[column],
                                                       downcast = 'unsigned')
                    except ValueError:
                        df[column] = pd.to_numeric(df[column],
                                                   downcast = 'float')
                elif self.datatypes[column] in ['categorical']:
                    df[column] = df[column].astype('category')
                elif self.datatypes[column] in ['list']:
                    df[column].apply(self.listify,
                                     axis = 'columns',
                                     inplace = True)
                elif self.datatypes[column] in ['datetime']:
                    df[column] = pd.to_datetime(df[column])
                elif self.datatypes[column] in ['timedelta']:
                    df[column] = pd.to_timedelta(df[column])
            else:
                error = column + ' is not in DataFrame'
                raise KeyError(error)
        return self

    @column_list
    @check_df
    def drop_columns(self, df = None, columns = None):
        """Drops list of columns and columns with prefixes listed. In addition,
        any dropped columns are stored in the cumulative dropped_columns
        list.

        Parameters:
            df: pandas DataFrame.
            columns: list of columns to drop.
            prefixes: list of prefixes for columns to drop.
            mask: numpy array, list, or pandas Series, of booleans of columns
                to drop.
        """
        df.drop(columns, axis = 'columns', inplace = True)
        self.dropped_columns.extend(columns)
        return self

    @column_list
    @check_df
    def drop_infrequent(self, df = None, columns = None, threshold = 0):
        """Drops boolean columns that rarely are True. This differs
        from the sklearn VarianceThreshold class because it is only
        concerned with rare instances of True and not False. This enables
        users to set a different variance threshold for rarely appearing
        information. threshold is defined as the percentage of total rows (and
        not the typical variance formulas used in sklearn).

        Parameters:
            df: a pandas DataFrame.
            columns: a list of columns to check. If not passed, all boolean
                columns will be used.
            threshold: a float indicating the percentage of True values in a
                boolean column that must exist for the column to be kept.
        """
        if not columns:
            columns = self.booleans
        infrequents = []
        for column in self.booleans:
            if column in columns:
                if df[column].mean() < threshold:
                    infrequents.append(column)
        self.drop_columns(columns = infrequents)
        return self

    @check_df
    def infer_datatypes(self, df = None):
        """Infers column datatypes and adds those datatypes to types. This
        method is an alternative to default pandas methods which can use
        complex datatypes (e.g., int8, int16, int32, int64, etc.). This also
        allows the user to choose which datatypes to look for by changing the
        default_values dictionary. Non-standard python datatypes cannot be
        inferred.

        Parameters:
            df: a pandas DataFrame.
        """
        if not self.datatypes:
            self.datatypes = {}
        for datatype in self.all_datatypes.values():
            type_columns = df.select_dtypes(
                include = [datatype]).columns.to_list()
            self.datatypes.update(
                dict.fromkeys(type_columns,
                              self.all_datatypes[datatype]))
        return self

    def prepare(self):
        """Prepares Ingredients class instance."""
        if self.verbose:
            print('Preparing ingredients')
        # If self.df is a path_name, the file located there is imported.
        if (not(isinstance(self.df, pd.DataFrame) or
                isinstance(self.df, pd.Series))
                and self.df and os.path.isfile(self.df)):
            self.load(name = 'df', file_path = self.df)
        # Initializes a list of dropped column names so that users can track
        # which features are omitted from analysis.
        self.dropped_columns = []
        # If datatypes passed, checks to see if columns are in df. Otherwise,
        # datatypes are inferred.
        self._initialize_datatypes()
        # Sets class for summarizing DataFrames in Ingredients.
        self.summarizer = Summary()
        return self

    def save_dropped(self, file_name = 'dropped_columns', file_format = 'csv'):
        """Saves dropped_columns into a file

        Parameters:
            file_name: string containing name of file to be exported.
            file_format: string of file extension from Inventory.extensions.
        """
        # Deduplicates dropped_columns list
        self.dropped_columns = self.deduplicate(self.dropped_columns)
        if self.dropped_columns:
            if self.verbose:
                print('Exporting dropped feature list')
            self.inventory.save(variable = self.dropped_columns,
                                folder = self.inventory.experiment,
                                file_name = file_name,
                                file_format = file_format)
        elif self.verbose:
            print('No features were dropped during preprocessing.')
        return

    @column_list
    @check_df
    def smart_fill(self, df = None, columns = None):
        """Fills na values in DataFrame to defaults based upon the datatype
        listed in the columns dictionary.

        Parameters:
            df: a pandas DataFrame.
            columns: list of columns to fill missing values in.
        """
        for column in self._check_columns(columns):
            if column in df:
                default_value = self.all_datatypes.default_values[
                        self.datatypes[column]]
                df[column].fillna(default_value, inplace = True)
            else:
                error = column + ' is not in DataFrame'
                raise KeyError(error)
        return self

    @check_df
    def split_xy(self, df = None, label = 'label'):
        """Splits df into x and y based upon the label passed.

        Parameters:
            df: a pandas DataFrame.
            label: name of column(s) to be stored in self.y
        """
        self.x = df.drop(label, axis = 'columns')
        self.y = df[label]
        # drops columns in self.y from datatypes dictionary.
        self._crosscheck_columns(df = self.x)
        return self

    @check_df
    def start(self, df = None):
        return df

    @check_df
    def summarize(self, df = None, transpose = True,
                  file_name = 'data_summary', file_format = 'csv'):
        """Creates and exports a DataFrame of common summary data using the
        Summary class.

        Parameters:
            df: a pandas DataFrame.
            transpose: boolean value indicating whether the df columns should
                be listed horizontally (True) or vertically (False) in report.
            file_name: string containing name of file to be exported.
            file_format: string of file extension from Inventory.extensions.
        """
        self.summarizer.start(df = df, transpose = transpose)
        if self.verbose:
            print('Saving ingredients summary data')
        self.inventory.save(variable = self.summarizer.report,
                            folder = self.inventory.experiment,
                            file_name = file_name,
                            file_format = file_format,
                            header = self.summarizer.df_header,
                            index = self.summarizer.df_index)
        return self
