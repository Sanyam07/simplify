
from dataclasses import dataclass

from simplify.core.base import SimplePlan


@dataclass
class Sow(SimplePlan):
    """Acquires and performs basic preparation of data sources.

    Args:
        steps(dict): dictionary containing keys of SimpleStep names (strings)
            and values of SimpleStep class instances.
        name(str): name of class for matching settings in the Idea instance
            and elsewhere in the siMpLify package.
        auto_finalize(bool): whether 'finalize' method should be called when
            the class is instanced. This should generally be set to True.
    """

    steps : object = None
    name : str = 'sower'
    auto_finalize : bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    def draft(self):
        self.options = {
                'download': ['simplify.farmer.steps.download', 'Download'],
                'scrape': ['simplify.farmer.steps.scrape', 'Scrape'],
                'convert': ['simplify.farmer.steps.convert', 'Convert'],
                'divide': ['simplify.farmer.steps.divide', 'Divide']}
        self.needed_parameters = {'convert' : ['file_in', 'file_out',
                                                 'method'],
                                  'download' : ['file_url', 'file_name'],
                                  'scrape' : ['file_url', 'file_name'],
                                  'split' : ['in_folder', 'out_folder',
                                                'method']}
        if self.technique in ['split']:
            self.import_folder = 'raw'
            self.export_folder = 'interim'
        else:
            self.import_folder = 'external'
            self.export_folder = 'external'
        return self

    def produce(self, ingredients):
        self.algorithm.produce(ingredients)
        return ingredients
