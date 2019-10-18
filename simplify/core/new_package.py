"""
.. module:: package
:synopsis: iterable builder and container
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from simplify.core.base import SimpleClass


@dataclass
class SimplePackage(SimpleClass, ABC):

    name: str = 'generic_package'
    steps: object = None
    plans: object = None
    options: object = None

    def __post_init__(self):
        super().__post_init__()
        return self

    @classmethod
    def create(cls, parameter_list):
        pass

