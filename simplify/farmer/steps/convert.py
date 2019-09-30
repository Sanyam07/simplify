
from dataclasses import dataclass
import os

from simplify.core.base import SimpleStep


@dataclass
class Convert(SimpleStep):
    """Converts data to a usable form.

    Args:
        technique(str): name of technique.
        parameters(dict): dictionary of parameters to pass to selected
            algorithm.
        name(str): name of class for matching settings in the Idea instance
            and elsewhere in the siMpLify package.
        auto_finalize(bool): whether 'finalize' method should be called when
            the class is instanced. This should generally be set to True.
    """

    technique : str = ''
    parameters : object = None
    name : str = 'converter'
    auto_finalize : bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    def _make_path(self, file_name):
        file_path = os.path.join(self.depot.external, file_name)
        return file_path

    def finalize(self):
        self.file_path_in = self.make_path(self.file_in)
        self.file_path_out = self.make_path(self.file_out)
        return self

    def produce(self, ingredients):
        converted = self.method(file_path = self.file_path_in)
        self.depot.save_df(converted, file_path = self.file_path_out)
        return self