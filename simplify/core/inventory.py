"""
.. module:: inventory
:synopsis: file management made simple
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from abc import ABC
from abc import abstractmethod
from collections.abc import MutableMapping
import csv
from dataclasses import dataclass
from dataclasses import field
import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import pandas as pd

from simplify.core.base import SimpleCatalog
from simplify.core.base import SimpleOutline
from simplify.core.states import create_states
from simplify.core.utilities import datetime_string
from simplify.core.utilities import deduplicate
from simplify.core.utilities import listify


@dataclass
class Inventory(MutableMapping):
    """Manages files and folders for siMpLify.

    Creates and stores dynamic and static file paths, properly formats files
    for import and export, and provides methods for loading and saving siMpLify,
    pandas, and numpy objects.

    Args:
        idea ('Idea'): ana instance with file-management related settings.
        root_folder (Optional[str]): the complete path from which the other
            paths and folders used by Inventory should be created. Defaults to
            the parent folder or the parent folder of the current working
            directory.
        data_folder (Optional[str]): the data subfolder name or a complete path
            if the 'data_folder' is not off of 'root_folder'. Defaults to
            'data'.
        data_subfolders (Optional[List[str]]): Defaults to a list of ['raw',
            'interim', 'processed', 'external'].
        results_folder (Optional[str]): the results subfolder name or a complete
            path if the 'results_folder' is not off of 'root_folder'. Defaults
            to 'results'.
        states (Optional[Union[List[str], 'SimpleState']]):

    """
    idea: 'Idea'
    root_folder: Optional[Union[str, List[str]]] = None
    data_folder: Optional[str] = 'data'
    data_subfolders: Optional[List[str]] = None
    results_folder: Optional[str] = 'results'
    states: Optional[Union[List[str], 'SimpleState']] = None

    def __post_init__(self) -> None:
        """Creates initial attributes."""
        # Uses defaults for 'data_subfolders, if not passed.
        self.data_subfolders = self.data_subfolders or [
            'raw',
            'interim',
            'processed',
            'external']
        # Injects attributes from 'idea'.
        self.idea_sections = ['files']
        self = self.idea.apply(instance = self)
        # Automatically calls 'draft' method to complete initialization.
        self.draft()
        return self

    """ Required ABC Methods """

    def __getitem__(self, key: str) -> Path:
        """Returns value for 'key' in 'folders'.

        Args:
            key (str): name of key in 'folders'.

        Returns:
            Path: item stored as a 'folders'.

        Raises:
            KeyError: if 'key' is not in 'folders'.

        """
        try:
            return self.folders[key]
        except KeyError:
            raise KeyError(' '.join([key, 'is not found in Inventory']))

    def __delitem__(self, key: str) -> None:
        """Deletes 'key' entry in 'folders'.

        Args:
            key (str): name of key in 'folders'.

        """
        try:
            del self.folders[key]
        except KeyError:
            pass
        return self

    def __setitem__(self, key: str, value: Any) -> None:
        """Sets 'key' in 'folders' to 'value'.

        Args:
            key (str): name of key in 'folders'.
            value (Any): value to be paired with 'key' in 'folders'.

        """
        self.folders[key] = value
        return self

    def __iter__(self) -> Iterable:
        """Returns iterable of 'folders'.

        Returns:
            Iterable stored in 'folders'.

        """
        return iter(self.folders.items())

    def __len__(self) -> int:
        """Returns length of 'folders'.

        Returns:
            Integer: length of 'folders'.

        """
        return len(self.folders)

    """ Private Methods """

    def _draft_root(self) -> None:
        """Turns 'root_folder' into a Path object."""
        self.root_folder = self.root_folder or ['..', '..']
        if isinstance(self.root_folder, list):
            root = Path.cwd()
            for item in self.root_folder:
                root = root.joinpath(item)
            self.folders['root'] = root
        else:
            self.folders['root'] = Path(self.root_folder)
        return self

    def _draft_core_folders(self) -> None:
        """Drafts initial data and results folders."""
        self.folders['results'] = self.folders['root'].joinpath(
            self.results_folder)
        self._write_folder(folder = self.folders['results'])
        self.folders['data'] = self.folders['root'].joinpath(
            self.data_folder)
        self._write_folder(folder = self.folders['data'])
        for folder in self.data_subfolders:
            self.folders['folder'] = self.folders['data'].joinpath(folder)
            self._write_folder(folder = self.folders['folder'])
        return self

    def _draft_file_formats(self) -> None:
        self.file_formats = SimpleCatalog(dictionary = {
            'csv': FileFormat(
                name = 'csv',
                module = 'pandas',
                extension = '.csv',
                import_method = 'read_csv',
                export_method = 'to_csv',
                additional_kwargs = [
                    'encoding',
                    'index_col',
                    'header',
                    'usecols',
                    'low_memory'],
                test_size_parameter = 'nrows'),
            'excel': FileFormat(
                name = 'excel',
                module = 'pandas',
                extension = '.xlsx',
                import_method = 'read_excel',
                export_method = 'to_excel',
                additional_kwargs = ['index_col', 'header', 'usecols'],
                test_size_parameter = 'nrows'),
            'feather': FileFormat(
                name = 'feather',
                module = 'pandas',
                extension = '.feather',
                import_method = 'read_feather',
                export_method = 'to_feather',
                required = {'nthreads': -1}),
            'hdf': FileFormat(
                name = 'hdf',
                module = 'pandas',
                extension = '.hdf',
                import_method = 'read_hdf',
                export_method = 'to_hdf',
                additional_kwargs = ['columns'],
                test_size_parameter = 'chunksize'),
            'json': FileFormat(
                name = 'json',
                module = 'pandas',
                extension = '.json',
                import_method = 'read_json',
                export_method = 'to_json',
                additional_kwargs = ['encoding', 'columns'],
                test_size_parameter = 'nrows'),
            'stata': FileFormat(
                name = 'stata',
                module = 'pandas',
                extension = '.dta',
                import_method = 'read_stata',
                export_method = 'to_stata',
                test_size_parameter = 'chunksize'),
            'text': FileFormat(
                name = 'text',
                module = None,
                extension = '.txt',
                import_method = '_import_text',
                export_method = '_export_text'),
            'png': FileFormat(
                name = 'png',
                module = 'seaborn',
                extension = '.png',
                export_method = 'save_fig',
                required = {'bbox_inches': 'tight', 'format': 'png'}),
            'pickle': FileFormat(
                name = 'pickle',
                module = None,
                extension = '.pickle',
                import_method = '_pickle_object',
                export_method = '_unpickle_object')})
        self.import_format_states = {
            'sow': 'source_format',
            'harvest': 'source_format',
            'clean': 'interim_format',
            'bale': 'interim_format',
            'deliver': 'interim_format',
            'chef': 'final_format',
            'actuary': 'final_format',
            'critic': 'final_format',
            'artist': 'final_format'}
        self.export_format_states = {
            'sow': 'source_format',
            'harvest': 'interim_format',
            'clean': 'interim_format',
            'bale': 'interim_format',
            'deliver': 'final_format',
            'chef': 'final_format',
            'actuary': 'final_format',
            'critic': 'final_format',
            'artist': 'final_format'}
        return self

    def _draft_file_names(self) -> None:
        self.import_file_names = {
            'sow': None,
            'harvest': None,
            'clean': 'harvested_data',
            'bale': 'cleaned_data',
            'deliver': 'baled_data',
            'chef': 'final_data',
            'actuary': 'final_data',
            'critic': 'final_data',
            'artist': 'predicted_data'}
        self.export_file_names = {
            'sow': 'source_format',
            'harvest': 'interim_format',
            'clean': 'interim_format',
            'bale': 'interim_format',
            'deliver': 'final_format',
            'chef': 'final_format',
            'actuary': 'final_data',
            'critic': 'predicted_data',
            'artist': 'predicted_data'}
        return self

    def _draft_folders(self) -> None:
        self.import_folders = {
            'sow': 'raw',
            'reap': 'raw',
            'clean': 'interim',
            'bale': 'interim',
            'deliver': 'interim',
            'chef': 'processed',
            'actuary': 'processed',
            'critic': 'processed',
            'artist': 'processed'}
        self.export_folders = {
            'sow': 'raw',
            'reap': 'interim',
            'clean': 'interim',
            'bale': 'interim',
            'deliver': 'processed',
            'chef': 'processed',
            'actuary': 'processed',
            'critic': 'processed',
            'artist': 'processed'}
        return self

    def _make_unique_path(self, folder: Path, name: str) -> Path:
        counter = 0
        while True:
            counter += 1
            path = folder / name.format(counter)
            if not path.exists():
                return path

    def _pathlibify(self,
            folder: str,
            name: Optional[str] = None,
            extension: Optional[str] = None) -> Path:
        """Converts strings to pathlib Path object.

        Args:


        Returns:
            Path: formed from string arguments.

        """
        try:
            folder = self.folders[folder]
        except (KeyError, TypeError):
            try:
                if folder.is_dir():
                    pass
            except (AttributeError, TypeError):
                folder = self.folders['root'].joinpath(folder)
        if name and extension:
            return folder.joinpath('.'.join([name, extension]))
        elif isinstance(folder, Path):
            return folder
        else:
            return Path(folder)

    def _write_folder(self, folder: str) -> None:
        """Writes folder to disk.

        Args:
            folder (str): writes folder to disk and any parent folders that are
                needed.

        """
        Path.mkdir(folder, parents = True, exist_ok = True)
        return self

    """ File Input/Output Methods """

    def load(self, file_path: str, file_format: str, **kwargs) -> Any:
        if self.file_formats[file_format].module in ['pandas', 'numpy']:
            importer = self.data_importer
        else:
            importer = self.results_importer
        return importer.load(
                file_path = file_path,
                file_format = file_format,
                **kwargs)

    def save(self, instance: Any, file_format: str, **kwargs) -> None:
        if self.file_formats[file_format].module in ['pandas', 'numpy']:
            exporter = self.data_exporter
        else:
            exporter = self.results_exporter
        exporter.save(instance = instance, file_format = file_format, **kwargs)
        return self

    def set_project_folder(self, name: Optional[str] = None) -> None:
        if name is None:
            name = '_'.join('project', datetime_string())
        self.folders['project'] = self.folders['results'].joinpath(name)
        return self

    def set_chapter_folder(self,
            prefix: Optional[str] = None,
            name: Optional[str] = None) -> None:
        prefix = prefix or 'chapter'
        if name:
            return self.folders['project'].joinpath('_'.join([prefix, name]))
        else:
            return self._make_unique_path(
                folder = self.folders['project'],
                name = '_'.join([prefix, '{:03d}']))

    """ Core siMpLify Methods """

    def draft(self) -> None:
        """Initializes core paths and attributes."""
        # Initializes 'state' for state management.
        self.state = create_states(states = self.states)
        # Initializes internal 'folders' dictionary.
        self.folders = {}
        # Transforms root folder path into a Path object.
        self._draft_root()
        # Creates basic folder structure and writes folders to disk.
        self._draft_core_folders()
        # Creates catalogs of file formats, folders, and file names.
        self._draft_file_formats()
        self._draft_folders()
        self._draft_file_names()
        # Creates importer and exporter instances for file management.
        self.data_importer = Importer(
            inventory = self,
            root_folder = self.data_folder,
            folders = self.import_folders,
            file_format_states = self.import_format_states,
            file_names = self.import_file_names)
        self.data_exporter = Exporter(
            inventory = self,
            root_folder = self.data_folder,
            folders = self.export_folders,
            file_format_states = self.export_format_states,
            file_names = self.export_file_names)
        self.results_importer = Importer(
            inventory = self,
            root_folder = self.data_folder)
        self.results_exporter = Exporter(
            inventory = self,
            root_folder = self.results_folder)
        return self


@dataclass
class SimpleDistributor(ABC):
    """Base class for siMpLify Importer and Exporter."""

    inventory: 'Inventory' = None

    def __post_init__(self) -> None:
        """Initializes class instance attributes."""
        # Creates 'Pathifier' instance for dynamic path creation.
        self.pathifier = Pathifier(
            inventory = self.inventory,
            distributor = self)
        return self

    """ Private Methods """

    def _check_kwargs(self,
            file_format: 'FileFormat',
            passed_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Selects kwargs for particular methods.

        If a needed argument was not passed, default values are used.

        Args:
            variables_to_check (List[str]): variables to check for values.
            passed_kwargs (Dict[str, Any]): kwargs passed to method.

        Returns:
            new_kwargs (Dict[str, Any]): kwargs with only relevant parameters.

        """
        new_kwargs = passed_kwargs
        for variable in file_format.addtional_kwargs:
            if not variable in passed_kwargs:
                if variable in self.inventory.default_kwargs:
                    new_kwargs.update(
                        {variable: self.inventory.default_kwargs[variable]})
                elif hasattr(self.inventory, variable):
                    new_kwargs.update(
                        {variable: getattr(self.inventory, variable)})
        return new_kwargs

    def _check_file_format(self,
            file_format: Union[str, 'FileFormat']) -> 'FileFormat':
        """Selects 'file_format' or default value.

        Args:
            file_format (Union[str, 'FileFormat']): name of file format or a
                'FileFormat' instance.

        Returns:
            str: completed file_format.

        """
        if isinstance(file_format, FileFormat):
            return file_format
        elif isinstance(file_format, str):
            return self.inventory.file_formats[file_format]
        else:
            return self.inventory.file_formats[
                self.file_formats[self.inventory.state]]

    def _make_parameters(self,
            file_format: 'FileFormat',
            **kwargs) -> Dict[str, Any]:
        parameters = self._check_kwargs(
            file_format = file_format,
            passed_kwargs = kwargs)
        try:
            parameters.update(file_format.required)
        except TypeError:
            pass
        if kwargs:
            parameters.update(**kwargs)
        return parameters


@dataclass
class Importer(SimpleDistributor):
    """Manages file importing for siMpLify.

    Args:
        inventory ('Inventory'): related Inventory instance.

    """
    inventory: 'Inventory' = None
    root_folder: Optional[str] = None
    folders: Optional[Dict[str, str]] = field(default_factory = dict)
    file_format_states: Optional[Dict[str, str]] = field(default_factory = dict)
    file_names: Optional[Dict[str, str]] = field(default_factory = dict)

    """ Public Methods """

    def load(self, **kwargs):
        return self.apply(**kwargs)

    def make_batch(self,
            folder: Optional[str] = None,
            file_format: Optional[str] = None,
            include_subfolders: Optional[bool] = True) -> Iterable[str]:
        """Creates a list of paths in 'folder_in' based upon 'file_format'.

        If 'include_subfolders' is True, subfolders are searched as well for
        matching 'file_format' files.

        Args:
            folder (Optional[str]): path of folder or string corresponding to
                class attribute with path.
            file_format (Optional[str]): file format name.
            include_subfolders (Optional[bool]): whether to include files in
                subfolders when creating a batch.

        """
        folder = folder or self.inventory[self.folders[self.inventory.stage]]
        file_format = self._check_file_format(file_format = file_format)
        if include_subfolders:
            return Path(folder).rglob('.'.join(['*', file_format.extension]))
        else:
            return Path(folder).glob('.'.join(['*', file_format.extension]))

    # def iterate_batch(self,
    #         chapters: List[str],
    #         ingredients: 'Ingredients' = None,
    #         return_ingredients: Optional[bool] = True):
    #     """Iterates through a list of files contained in self.batch and
    #     applies the chapters created by a book method (or subclass).
    #     Args:
    #         chapters(list): list of chapter types (Recipe, Harvest, etc.)
    #         ingredients(Ingredients): an instance of Ingredients or subclass.
    #         return_ingredients(bool): whether ingredients should be returned by
    #         this method.
    #     Returns:
    #         If 'return_ingredients' is True: an in instance of Ingredients.
    #         If 'return_ingredients' is False, no value is returned.
    #     """
    #     if ingredients:
    #         for file_path in self.batch:
    #             ingredients.source = self.load(file_path = file_path)
    #             for chapter in chapters:
    #                 data = chapter.produce(data = ingredients)
    #         if return_ingredients:
    #             return ingredients
    #         else:
    #             return self
    #     else:
    #         for file_path in self.batch:
    #             for chapter in chapters:
    #                 chapter.produce()
    #         return self

    """ Core siMpLify Methods """

    def apply(self,
            file_path: Optional[str],
            folder: Optional[str] = None,
            file_name: Optional[str] = None,
            file_format: Optional[Union[str, 'FileFormat']] = None,
            **kwargs) -> Any:
        """Imports file by calling appropriate method based on file_format.

        If needed arguments are not passed, default values are used. If
        file_path is passed, folder and file_name are ignored.

        Args:
            file_path (str): a complete file path for the file to be loaded.
            file_format ('FileFormat'): object with information about how the
                file should be loaded.
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        Returns:
            Any: depending upon method used for appropriate file format, a new
                variable of a supported type is returned.

        """
        file_format = self._check_file_format(file_format = file_format)
        file_path = self.pathifier.apply(
            file_path = file_path,
            folder = folder,
            file_name = file_name,
            file_format = file_format)
        if file_format.module:
            tool = file_format.load('import_method')
        else:
            tool = getattr(self, file_format.import_method)
        parameters = self._make_parameters(file_format = file_format, **kwargs)
        if sample_size:
            parameters[file_format.sample_size_parameter] = sample_size
        return tool(file_path, **parameters)


@dataclass
class Exporter(SimpleDistributor):
    """Manages file exporting for siMpLify.

    Args:
        inventory ('Inventory'): related Inventory instance.

    """
    inventory: 'Inventory' = None
    root_folder: Optional[str] = None
    folders: Optional[Dict[str, str]] = field(default_factory = dict)
    file_format_states: Optional[Dict[str, str]] = field(default_factory = dict)
    file_names: Optional[Dict[str, str]] = field(default_factory = dict)

    """ Private Methods """

    def _check_boolean_out(self,
            data: Union[pd.Series, pd.DataFrame]) -> (
                Union[pd.Series, pd.DataFrame]):
        """Converts True/False to 1/0 if 'boolean_out' is False.

        Args:
            data (Union[DataFrame, Series]): pandas object with some boolean
                values.

        Returns:
            data (Union[DataFrame, Series]): either the original pandas data or
                the dataset with True/False converted to 1/0.

        """
        # Checks whether True/False should be exported in data files. If
        # 'boolean_out' is set to False, 1/0 are used instead.
        if not self.inventory.boolean_out:
            data.replace({True: 1, False: 0}, inplace = True)
        return data

    """ Public Methods """

    # def initialize_writer(self,
    #         file_path: str,
    #         columns: List[str],
    #         encoding: Optional[str] = None,
    #         dialect: Optional[str] = 'excel') -> None:
    #     """Initializes writer object for line-by-line exporting to a .csv file.

    #     Args:
    #         file_path (str): a complete path to the file being written to.
    #         columns (List[str]): column names to be added to the first row of
    #             the file as column headers.
    #         encoding (str): a python encoding type.
    #         dialect (str): the specific type of csv file created. Defaults to
    #             'excel'.

    #     """
    #     if not columns:
    #         error = 'initialize_writer requires columns as a list type'
    #         raise TypeError(error)
    #     with open(file_path, mode = 'w', newline = '',
    #               encoding = self.file_encoding) as self.output_series:
    #         self.writer = csv.writer(self.output_series, dialect = dialect)
    #         self.writer.writerow(columns)
    #     return self

    # def iterate_writer(self):
    #     return self


    def save(self, **kwargs):
        return self.apply(**kwargs)

    """ Core siMpLify Methods """

    def apply(self,
            variable: Any,
            file_path: str,
            folder: Optional[str] = None,
            file_name: Optional[str] = None,
            file_format: Optional[Union[str, 'FileFormat']] = None,
            **kwargs) -> None:
        """Exports file by calling appropriate method based on file_format.

        If needed arguments are not passed, default values are used. If
        file_path is passed, folder and file_name are ignored.

        Args:
            variable (Any): the variable being exported.
            file_path (str): a complete file path for the file to be saved.
            file_format ('FileFormat'): object with information about how the
                file should be saved.
            **kwargs: can be passed if additional options are desired specific
                to the pandas or python method used internally.

        """
        file_format = self._check_file_format(file_format = file_format)
        file_path = self.pathifier.apply(
            file_path = file_path,
            folder = folder,
            file_name = file_name,
            file_format = file_format)
        # Changes boolean values to 1/0 if 'boolean_out' is False.
        if file_format.module in ['pandas']:
            variable = self._check_boolean_out(data = variable)
        if file_format.module:
            tool = file_format.load('export_method')
        else:
            tool = getattr(self, file_format.export_method)
        parameters = self._make_parameters(file_format = file_format, **kwargs)
        tool(variable, file_path, **parameters)
        return self


@dataclass
class Pathifier(object):
    """Builds file_paths based upon state.

    Args:
        inventory ('Inventory): related 'Inventory' instance.
        distributor ('SimpleDistributor'): related 'SimpleDistributor' instance.

    """
    inventory: 'Inventory'
    distributor: 'SimpleDistributor'

    def __post_init__(self) -> None:
        return self

    """ Private Methods """

    def _check_folder(self, folder: Optional[str] = None) -> str:
        """Selects 'folder' or default value.

        Args:
            folder (Optional[str]): name of folder. Defaults to None.

        Returns:
            str: completed file_name.

        """
        if not folder:
            return self.inventory.folders[self.distributor.folders[
                self.inventory.state]]
        else:
            try:
                return self.inventory.folders[folder]
            except AttributeError:
                if isinstance(folder, str):
                    return Path(folder)
                else:
                    return folder

    def _check_file_name(self, file_name: Optional[str] = None) -> str:
        """Selects 'file_name' or default value.

        Args:
            file_name (Optional[str]): name of file. Defaults to None.

        Returns:
            str: completed file_name.

        """
        if not file_name:
            return self.distributor.file_names[self.inventory.state]
        else:
            return file_name

    def _make_path(self,
            folder: str,
            file_name: str,
            file_format: str) -> str:
        """Creates completed file_path from passed arguments.

        Args:
            folder (str): name of target folder.
            file_name (str): name of file.
            file_format (str): name of file format.

        Returns:
            str: completed file path.

        """
        return folder.joinpath('.'.join([file_name, file_format.extension]))

    """ Core siMpLify Methods """

    def apply(self,
            file_path: Optional[str] = None,
            folder: Optional[str] = None,
            file_name: Optional[str] = None,
            file_format: 'FileFormat' = None) -> Path:
        """Creates file path from passed arguments.

        Args:
            file_path (Optional[str]): full file path. Defaults to None.
            folder (Optional[str]): name of target folder (not used if
                'file_path' passed). Defaults to None.
            file_name (Optional[str]): name of file (not used if 'file_path'
                passed). Defaults to None.
            file_format (Optional[str]): name of file format (not used if '
                file_path' passed). Defaults to None.

        Returns:
            str of completed file path.

        """
        if isinstance(file_path, Path):
            return file_path
        elif isinstance(file_path, str):
            return Path(file_path)
        else:
            return self._make_path(
                folder = self._check_folder(folder = folder),
                file_name = self._check_file_name(file_name = file_name),
                file_format = file_format)


@dataclass
class FileFormat(SimpleOutline):
    """File format container."""

    name: str
    module: str
    extension: Optional[str] = None
    import_method: Optional[str] = None
    export_method: Optional[str] = None
    additional_kwargs: Optional[List[str]] = None
    required: Optional[Dict[str, Any]] = None
    test_size_parameter: Optional[str] = None


""" Validator Function """

def create_inventory(
        inventory: Union['Inventory', str],
        idea: 'Idea') -> 'Inventory':
    """Creates an Inventory instance from passed arguments.

    Args:
        inventory: Union['Inventory', str]: Inventory instance or root folder
            for one.
        idea ('Idea'): an Idea instance.

    Returns:
        Inventory instance, properly configured.

    Raises:
        TypeError if inventory is neither an Inventory instance nor string
            folder path.

    """
    if isinstance(inventory, Inventory):
        return inventory
    elif isinstance(inventory, (str, Path)):
        return Inventory(idea = idea, root_folder = inventory)
    else:
        raise TypeError('inventory must be Inventory type or folder path')