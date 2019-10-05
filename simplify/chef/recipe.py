"""
.. module:: recipe
:synopsis: stores steps for data analysis and machine learning
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

from simplify.core.iterables import SimplePlan


@dataclass
class Recipe(SimplePlan):
    """Contains steps for analyzing data in the siMpLify Cookbook subpackage.

    Args:
        number(int): number of recipe in a sequence - used for recordkeeping
            purposes.
        steps(dict): dictionary containing keys of SimpleTechnique names (strings)
            and values of SimpleTechnique class instances.
        name(str): name of class for matching settings in the Idea instance
            and elsewhere in the siMpLify package.
        auto_publish(bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.
        auto_publish: bool = True

    """

    number: int = 0
    steps: object = None
    name: str = 'recipe'
    auto_publish: bool = True

    def __post_init__(self):
        self.idea_sections = ['chef']
        super().__post_init__()
        return self

    def draft(self):
        super().draft()
        self.iterable = 'steps'
        return self
    
    def implement(self, ingredients):
        """Applies the Cookbook steps to the passed ingredients."""
        steps = self.steps.copy()
        self.ingredients = ingredients
        self.ingredients.split_xy(label = self.label)
        # If using cross-validation or other data splitting technique, the
        # pre-split methods apply to the 'x' data. After the split, steps
        # must incorporate the split into 'x_train' and 'x_test'.
        for step in list(steps.keys()):
            steps.pop(step)
            if step == 'split':
                break
            else:
                self.ingredients = self.steps[step].implement(
                    ingredients = self.ingredients,
                    plan = self)
        split_algorithm = self.steps['split'].algorithm
        for train_index, test_index in split_algorithm.split(
                self.ingredients.x, self.ingredients.y):
            self.ingredients.x_train, self.ingredients.x_test = (
                   self.ingredients.x.iloc[train_index],
                   self.ingredients.x.iloc[test_index])
            self.ingredients.y_train, self.ingredients.y_test = (
                   self.ingredients.y.iloc[train_index],
                   self.ingredients.y.iloc[test_index])
            for step, technique in steps.items():
                self.ingredients = technique.implement(
                       ingredients = self.ingredients,
                       plan = self)
        return self
