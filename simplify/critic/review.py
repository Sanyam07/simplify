"""
.. module:: review
:synopsis: core classes for Critic subpackage.
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

import pandas as pd

from simplify.core.base import SimpleManager
from simplify.core.decorators import localize


@dataclass
class Review(SimpleManager):
    """Builds tools for evaluating, explaining, and creating predictions from
    data and machine learning models.

    Args:
        idea(Idea or str): an instance of Idea or a string containing the file
            path or file name (in the current working directory) where a 
            supoorted settings file for an Idea instance is located.
        depot(Depot): an instance of Depot.
        ingredients(Ingredients): an instance of Ingredients. This argument need
            not be passed when the class is instanced. It can be passed directly
            to the 'produce' method as well.
        steps(dict(str: SimpleStep)): names and related SimpleStep classes for
            analyzing fitted models.
        recipes(Recipe or list(Recipe)): a list or single Recipe to be reviewed.
            This argument need not be passed when the class is instanced. It
            can be passed directly to the 'produce' method as well.
        name(str): designates the name of the class which should be identical
            to the section of the idea configuration with relevant settings.
        auto_finalize(bool): whether to call the 'finalize' method when the
            class is instanced.
        auto_produce(bool): whether to call the 'produce' method when the class
            is instanced.
            
    Since this class is a subclass to SimpleManager and SimpleClass, all
    documentation for those classes applies as well.
    
    """
    idea: object = None
    depot: object = None
    ingredients: object = None
    steps: object = None
    recipes: object = None
    name: str = 'review'
    auto_finalize: bool = True
    auto_produce: bool = False

    def __post_init__(self):
        super().__post_init__()
        return self

    """ Private Methods """

    def _check_best(self, recipe):
        """Checks if the current recipe is better than the current best recipe
        based upon the primary scoring metric.

        Args:
            recipe: an instance of Recipe to be tested versus the current best
                recipe stored in the 'best_recipe' attribute.
        """
        if not hasattr(self, 'best_recipe') or self.best_recipe is None:
            self.best_recipe = recipe
            self.best_recipe_score = self.report.loc[
                    self.report.index[-1],
                    self.listify(self.metrics)[0]]
        elif (self.report.loc[
                self.report.index[-1],
                self.listify(self.metrics)[0]] > self.best_recipe_score):
            self.best_recipe = recipe
            self.best_recipe_score = self.report.loc[
                    self.report.index[-1],
                    self.listify(self.metrics)[0]]
        return self

    def _check_technique_name(self, step):
        """Returns appropriate algorithm to the report attribute."""
        if step.technique in ['none', 'all']:
            return step.technique
        else:
            return step.algorithm

    def _finalize_report(self):
        self._set_columns()
        self.report = pd.DataFrame(columns = self.columns)
        return self

    def _format_step(self, attribute):
        if getattr(self.recipe, attribute).technique in ['none', 'all']:
            step_column = getattr(self.recipe, attribute).technique
        else:
            technique = getattr(self.recipe, attribute).technique
            parameters = getattr(self.recipe, attribute).parameters
            step_column = f'{technique}, parameters = {parameters}'
        return step_column

    def _set_columns(self):
        self.columns = {'recipe_number': 'number',
                        'options': 'techniques',
                        'seed': 'seed',
                        'validation_set': 'val_set'}
        self.columns = list(self.columns_map.keys())
        for number, instance in getattr(self, self.plan_iterable).items():
            if hasattr(instance, 'columns'):
                self.columns.extend(instance.columns)
        return self


    """ Public Tool Methods """

    def print_best(self):
        """Prints output to the console about the best recipe."""
        if self.verbose:
            print('The best test recipe, based upon the',
                  self.listify(self.metrics)[0], 'metric with a score of',
                  f'{self.best_recipe_score: 4.4f}', 'is:')
            for technique in getattr(self,
                    self.plan_iterable).best_recipe.techniques:
                print(technique.capitalize(), ':',
                      getattr(getattr(self, self.plan_iterable).best_recipe,
                              technique).technique)
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
        # Sets 'manager_type' so that proper parent methods are used.
        self.manager_type = 'serial'
        # Sets plan-related attributes to allow use of parent methods.
        self.plan_iterable = 'reviews'
        self.columns_map = {'recipe_number': 'number',
                            'options': 'techniques',
                            'seed': 'seed',
                            'validation_set': 'val_set'}
        return self

    def finalize(self):
        super().finalize()
        self._finalize_report()
        return self

    @localize
    def produce(self, recipes = None, ingredients = None):
        """Evaluates recipe with various tools and finalizes report.

        Args:
            ingredients (Ingredients): an instance or subclass instance of
                Ingredients.
            recipes (list or Recipe): a Recipe or a list of Recipes.
        """
         if self.ingredients is None:
            self.ingredients = self.recipes.ingredients
        for recipe in self.listify(recipes):
            if self.verbose:
                print('Testing', recipe.name, str(recipe.number))
            self._check_best(recipe = recipe)
            row = pd.Series(index = self.columns)
            for column, value in self.columns.items():
                if isinstance(getattr(recipe, value), object):
                    row[column] = self._format_step(value)
                else:
                    row[column] = getattr(self.recipe, value)
            self.report.loc[len(self.report)] = row
        return self