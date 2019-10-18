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
class SimpleCreator(SimpleClass):

    name: str = 'class_factory'
    options: object = None
    steps: object = None
    plans: object = None
    technique: object = None
    parameters: object = None
    auto_draft: bool = True
    auto_publish: bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    @abstractmethod
    @classmethod
    def create(cls, **kwargs):
        pass

class SimpleTechnique(SimpleCreator):

    name: str = 'generic_technique'
    options: object = None
    technique: object = None
    parameters: object = None
    auto_draft: bool = True
    auto_publish: bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    @classmethod
    def create(cls, **kwargs):
        pass

    def draft(self):
        return self

    def publish(self):
        return self


