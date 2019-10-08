"""
.. module:: review
:synopsis: core classes for Critic subpackage.
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

import pandas as pd

#from simplify.core.decorators import localize
from simplify.core.iterable import SimpleIterable



@dataclass
class Review(SimpleIterable):
    """Builds tools for evaluating, explaining, and creating predictions from
    data and machine learning models.

    Args:
        ingredients(Ingredients or str): an instance of Ingredients of a string
            containing the full file path of where a supported file type that
            can be loaded into a pandas DataFrame is located. If it is a string,
            the loaded DataFrame will be bound to a new ingredients instance as
            the 'df' attribute.
        steps(dict(str: SimpleIterable)): names and related SimpleIterable
            classes for analyzing fitted models.
        recipes(Recipe or list(Recipe)): a list or single Recipe to be reviewed.
            This argument need not be passed when the class is instanced. It
            can be passed directly to the 'implement' method as well.
        name(str): designates the name of the class which should be identical
            to the section of the idea configuration with relevant settings.
        auto_publish(bool): whether to call the 'publish' method when the
            class is instanced.
        auto_implement(bool): whether to call the 'implement' method when the
            class is instanced.

    Since this class is a subclass to SimpleIterable and SimpleClass, all
    documentation for those classes applies as well.

    """

    ingredients: object = None
    steps: object = None
    recipes: object = None
    name: str = 'critic'
    auto_publish: bool = True
    auto_implement: bool = False

    def __post_init__(self):
        super().__post_init__()
        return self

    """ Private Methods """

    def _format_step(self, attribute):
        if getattr(self.recipe, attribute).technique in ['none', 'all']:
            step_column = getattr(self.recipe, attribute).technique
        else:
            technique = getattr(self.recipe, attribute).technique
            parameters = getattr(self.recipe, attribute).parameters
            step_column = f'{technique}, parameters = {parameters}'
        return step_column

    def _get_technique_name(self, step):
        """Returns appropriate algorithm to the report attribute."""
        if step.technique in ['none', 'all']:
            return step.technique
        else:
            return step.algorithm

    def _set_columns(self, recipe):
        self.required_columns = {
            'recipe_number': 'number',
            'options': 'techniques',
            'seed': 'seed',
            'validation_set': 'val_set'}
        self.columns = list(self.required_columns.keys())
        self.columns.extend(list(recipe.steps.keys()))
        for number, instance in getattr(self, self.iterator).items():
            if hasattr(instance, 'columns') and instance.name != 'summarize':
                self.columns.extend(instance.columns)
        return self

    def _start_report(self, recipe):
        self._set_columns(recipe = recipe)
        self.report = pd.DataFrame(columns = self.columns)
        return self

    """ Public Import/Export Methods """

    def save(self, report = None):
        """Exports the review report to disc.

        Args:
            review(Review.report): 'report' from an instance of review
        """
        self.depot.save(variable = report,
                        folder = self.depot.experiment,
                        file_name = self.model_type + '_review',
                        file_format = 'csv',
                        header = True)
        return

    """ Core siMpLify methods """

    def draft(self):
        """Sets default options for the Critic's analysis."""
        super().draft()
        self.options = {
            'summarize': ['simplify.critic.summarize', 'Summarize'],
            'explain': ['simplify.critic.explain', 'Explain'],
            'rank': ['simplify.critic.rank', 'Rank'],
            'predict': ['simplify.critic.predict', 'Predict'],
            'score': ['simplify.critic.score', 'Score']}
        # Locks 'step' attribute at 'critic' for conform methods in package.
        self.step = 'critic'
        # Sets iterable-related attributes.
        self.iterator = 'reviews'
        self.iterable_setting = 'review_steps'
        self.iterable_type = 'serial'
        self.return_variables = {
            'summarize': ['summary'],
            'explain': ['values'],
            'rank': ['importances'],
            'predict': ['predictions, probabilities'],
            'score': ['report']}
        return self

    def publish(self):
        super().publish()
        return self

    def implement(self, ingredients = None, recipes = None):
        """Evaluates recipe with various tools and publishs report.

        Args:
            ingredients (Ingredients): an instance or subclass instance of
                Ingredients.
            recipes (list or Recipe): a Recipe or a list of Recipes.
        """
        # Sets local 'ingredients' attribute.
        if self.ingredients is None and hasattr(recipes, 'ingredients'):
            self.ingredients = recipes.ingredients
        # Initializes comparative model report with set columns.
        if not self.exists('report'):
            self._start_report(recipe = self.listify(recipes)[0])
        # Iterates through 'recipes' to gather review information.
        for self.recipe in self.listify(recipes):
            if self.verbose:
                print('Reviewing', self.recipe.name, str(self.recipe.number))
            for name, technique in getattr(self, self.iterator).items():
                technique.implement(ingredients = ingredients,
                                    recipes = recipes)
                if self.exists('return_variables'):
                    self._get_return_variables(instance = technique)
        return self