"""
.. module:: siMpLify
:synopsis: data science made simple
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from simplify import creator
from simplify.__main__ import main as project
from simplify.core.project import Project
from simplify.core.utilities import timer


__version__ = '0.1.1'

__author__ = 'Corey Rayburn Yung'

__all__ = ['creator',
           'project',
           'Project',
           'timer']