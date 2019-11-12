"""
.. module:: scrape
:synopsis: data scraper
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass
import os

from simplify.core.technique import FarmerTechnique


@dataclass
class Scrape(FarmerTechnique):
    """Scrapes data from a website.

    Args:
        technique(str): name of technique.
        parameters(dict): dictionary of parameters to pass to selected
            algorithm.
        name(str): name of class for matching settings in the Idea instance
            and elsewhere in the siMpLify package.
        auto_draft(bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.
    """

    technique: object = None
    parameters: object = None
    name: str = 'converter'
    auto_draft: bool = True

    def __post_init__(self) -> None:
        super().__post_init__()
        return self


    def publish(self, ingredients):
        file_path = os.path.join(self.depot.external, self.file_name)
        return self
