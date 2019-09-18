"""
cookbook.py is the primary control file for the siMpLify machine learning
package. 

Contents:

    Cookbook: class which handles construction and utilization of recipes of
        limited preprocessing and machine learning of data in the siMpLify
        package.
    Recipe: class which stores a particular set of techniques and algorithms
        of limited preprocessing and machine learning operations.
        
    Both classes are subclasses to SimpleClass and follow its structural rules.
    
"""
from dataclasses import dataclass
import datetime
from itertools import product

from simplify.chef.steps import (Cleave, Encode, Mix, Model, Reduce, Sample,
                                 Scale, Split)
from simplify.core.decorators import check_arguments
from simplify.core.base import SimpleManager
from simplify.critic.analysis import Analysis


@dataclass
class Cookbook(SimpleManager):
    """Dynamically creates recipes for staging, machine learning, and data
    analysis using a unified interface and architecture.

    Args:
        ingredients: an instance of Ingredients (or a subclass). This argument
            does not need to be passed when the class is instanced. However,
            failing to do so will prevent the use of the Cleave step and the
            _compute_hyperparameters method. 'ingredients' will need to be 
            passed to the 'produce' method if it isn't when the class is
            instanced. Consequently, it is recommended that 'ingredients' be
            passed when the class is instanced.
        steps: a list of string step names to be completed in order. This 
            argument should only be passed if the user wishes to override the 
            steps listed in the Idea settings or if the user is not using the
            Idea class.
        recipes: a list of instances of Recipe which Cookbook creates through
            the 'finalize' method and applies through the 'produce' method.
            Ordinarily, 'recipes' is not passed when Cookbook is instanced, but
            the argument is included if the user wishes to reexamine past
            recipes or manually create new recipes.
        name: a string designating the name of the class which should be
            identical to the section of the Idea section with relevant settings.
        auto_finalize: sets whether to automatically call the 'finalize' method
            when the class is instanced. If you do not plan to make any
            adjustments to the steps, techniques, or algorithms beyond the
            Idea configuration, this option should be set to True. If you plan
            to make such changes, 'finalize' should be called when those changes
            are complete.
        auto_produce: sets whether to automatically call the 'produce' method
            when the class is instanced.
    """
    ingredients : object = None
    steps : object = None
    recipes : object = None
    name : str = 'cookbook'
    auto_finalize : bool = True
    auto_produce : bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    """ Private Methods """

    def _compute_hyperparameters(self):
        """Computes hyperparameters that can be determined by the source data
        (without creating data leakage problems).
        
        This method currently only support xgboost's scale_pos_weight
        parameter. Future hyperparameter computations will be added as they
        are discovered.
        """
        # 'ingredients' attribute is required before method can be called.
        if self.ingredients is not None:
            # Data is split in oder for certain values to be computed that
            # require features and the label to be split.
            self.ingredients.split_xy(label = self.label)
            # Model class is injected with scale_pos_weight for algorithms that
            # use that parameter.
            Model.scale_pos_weight = (len(self.ingredients.y.index) /
                                    ((self.ingredients.y == 1).sum())) - 1
        return self

    def _produce_recipes(self):
        for recipe_number, recipe in getattr(self, self.plan_iterable).items():
            if self.verbose:
                print('Testing', recipe.name, str(recipe_number))
            recipe.produce(ingredients = self.ingredients)
            self.save_recipe(recipe = recipe)
            self.analysis.produce(recipes = recipe)  
        return self 
        
    def _set_experiment_folder(self):
        """Sets the experiment folder and corresponding attributes in this
        class's Depot instance based upon user settings.
        """
        if self.depot.datetime_naming:
            subfolder = ('experiment_'
                         + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M'))
        else:
            subfolder = 'experiment'
        self.depot.experiment = self.depot.create_folder(
                folder = self.depot.results, subfolder = subfolder)
        return self

    def _set_recipe_folder(self, recipe):
        """Creates file or folder path for plan-specific exports.

        Args:
            plan: an instance of Almanac or Recipe for which files are to be
                saved.
            steps to use: a list of strings or single string containing names
                of steps from which the folder name should be created.
        """
        if hasattr(self, 'naming_classes') and self.naming_classes is not None:
            subfolder = 'recipe_'
            for step in self.listify(self.naming_classes):
                subfolder += recipe.techniques[step].technique + '_'
            subfolder += str(recipe.number)
            self.depot.recipe = self.depot.create_folder(
                folder = self.depot.experiment, subfolder = subfolder)
        return self

    """ Public Methods """

    def add_cleaves(self, cleave_group, prefixes = None, columns = None):
        """Adds cleaves to the list of cleaves.

        Args:
            cleave_group: string naming the set of features in the group.
            prefixes: list or string of prefixes for columns to be included
                within the cleave.
            columns: list or string of columns to be included within the
                cleave."""
        if not hasattr(self, 'cleaves') or self.cleaves is None:
            self.cleaves = []
        columns = self.ingredients.create_column_list(prefixes = prefixes,
                                                      columns = columns)
        Cleave.add(cleave_group = cleave_group, columns = columns)
        self.cleaves.append(cleave_group)
        return self

    def draft(self):
        """ Declares default step names and plan_class in a Cookbook recipe."""
        # Sets options for default steps of a Recipe.
        self.options = {'scaler' : Scale,
                        'splitter' : Split,
                        'encoder' : Encode,
                        'mixer' : Mix,
                        'cleaver' : Cleave,
                        'sampler' : Sample,
                        'reducer' : Reduce,
                        'model' : Model}
        # Adds GPU check to other checks to be produceed.
        self.checks = ['gpu', 'idea', 'steps', 'ingredients']
        # Locks 'step' attribute at 'cook' for conform methods in package.
        self.step = 'cook'
        # Sets attributes to allow proper parent methods to be used.
        self.manager_type = 'parallel'
        self.plan_class = Recipe
        self.plan_iterable = 'recipes'
        return self

    def edit_recipes(self, recipes):
        """Adds a single recipe or list of recipes to 'recipes' attribute.

        Args:
            recipe: an instance of Recipe.
        """
        if hasattr(self, 'recipes'):
            self.recipes.extend(self.listify(recipes))
        else:
            self.recipes = self.listify(recipes)
        return self

    def finalize(self):
        """Creates a planner with all possible selected permutations of
        methods. Each set of methods is stored in a list of instances of the
        class stored in self.recipes.
        """
        # Sets attributes for data analysis and export.
        self.analysis = Analysis()
        self._set_experiment_folder()
        # Creates all recipe combinations and store Recipe instances in 
        # 'recipes'.
        self._finalize_parallel()
        return self

    def load_recipe(self, file_path):
        """Imports a single recipe from disc and adds it to self.recipes.

        Args:
            file_path: a path where the file to be loaded is located.
        """
        self.edit_recipes(recipe = self.depot.load(file_path = file_path,
                                                   file_format = 'pickle'))
        return self

    def print_best(self):
        """Calls critic instance print_best method. The method is added here
        for easier accessibility.
        """
        self.analysis.print_best()
        return self

    @check_arguments
    def produce(self, ingredients = None):
        """Completes an iteration of a Cookbook.

        Args:
            ingredients: an Instance of Ingredients. If passsed, it will be
                assigned to self.ingredients. If not passed, and if it already
                exists, self.ingredients will be used.
        """
        if ingredients:
            self.ingredients = ingredients
        if 'train_test_val' in self.data_to_use:
            self.ingredients._remap_dataframes(data_to_use = 'train_test')
            self._produce_recipes()
            self.ingredients._remap_dataframes(data_to_use = 'train_val')
            self._produce_recipes()
        else:
            self.ingredients._remap_dataframes(data_to_use = self.data_to_use)
            self._produce_recipes()
        return self
        
    def save_all_recipes(self):
        """Saves all recipes in self.recipes to disc as individual files."""
        for recipe in self.recipes:
            file_name = (
                'recipe' + str(recipe.number) + '_' + recipe.model.technique)
            self.save_recipe(recipe = recipe,
                             folder = self.depot.recipe,
                             file_name = file_name,
                             file_format = 'pickle')
        return

    def save_best_recipe(self):
        """Saves the best recipe to disc."""
        if hasattr(self, 'best_recipe'):
            self.depot.save(variable = self.best_recipe,
                            folder = self.depot.experiment,
                            file_name = 'best_recipe',
                            file_format = 'pickle')
        return

    def save_everything(self):
        """Automatically saves the recipes, results, dropped columns from
        ingredients, and the best recipe (if one has been stored)."""
        self.save()
        self.save_review()
        self.save_best_recipe()
        self.ingredients.save_dropped()
        return

    def save_recipe(self, recipe, file_path = None):
        """Exports a recipe to disc.

        Args:
            recipe: an instance of Recipe.
            file_path: path of where file should be saved. If none, a default
                file_path will be created from self.depot."""
        if self.verbose:
            print('Saving recipe', recipe.number)
        self._set_recipe_folder(recipe = recipe)
        self.depot.save(variable = recipe,
                        file_path = file_path,
                        folder = self.depot.recipe,
                        file_name = 'recipe',
                        file_format = 'pickle')
        return

    def save_review(self, review = None):
        """Exports the Analysis review to disc.

        Args:
            review: the attribute review from an instance of Analysis. If none
                is provided, self.analysis.review is saved.
        """
        if not review:
            review = self.analysis.review.report
        self.depot.save(variable = review,
                        folder = self.depot.experiment,
                        file_name = self.model_type + '_review',
                        file_format = 'csv',
                        header = True)
        return


@dataclass
class Recipe(SimpleManager):
    """Defines rules for analyzing data in the siMpLify Cookbook subpackage.

    Attributes:
        techniques(dict): techniques containing the classes to be used at
            each stage of a Recipe.
        name: a string designating the name of the class which should be
            identical to the section of the idea with relevant settings.
    """
    techniques : object = None
    name : str = 'recipe'

    def __post_init__(self):
        self.idea_sections = ['cookbook']
        super().__post_init__()
        return self

    def __call__(self, *args, **kwargs):
        """When called as a function, a Recipe class or subclass instance will
        return the produce method.
        """
        return self.produce(*args, **kwargs)

    def draft(self):
        pass
        return self
        
    def finalize(self):
        pass
        return self

    def produce(self, ingredients):
        """Applies the Recipe methods to the passed ingredients."""
        techniques = self.techniques.copy()
        self.ingredients = ingredients
        ingredients.split_xy(label = self.label)
        # If using cross-validation or other data splitting technique, the 
        # pre-split methods apply to the 'x' data. After the split, techniques
        # must be incorporate the split into 'x_train' and 'x_test'.
        for step in list(techniques.keys()):
            techniques.pop(step)
            if step == 'splitter':
                break
            else:
                self.ingredients = self.techniques[step].produce(
                    ingredients = self.ingredients,
                    recipe = self)
        split_algorithm = self.techniques['splitter'].algorithm
        for train_index, test_index in split_algorithm.split(
                self.ingredients.x, self.ingredients.y):
           self.ingredients.x_train, self.ingredients.x_test = (
                   self.ingredients.x.iloc[train_index],
                   self.ingredients.x.iloc[test_index])
           self.ingredients.y_train, self.ingredients.y_test = (
                   self.ingredients.y.iloc[train_index],
                   self.ingredients.y.iloc[test_index])
           for step, technique in techniques.items():
                self.ingredients = technique.produce(
                    ingredients = self.ingredients,
                    recipe = self)
        return self