import os

import pandas as pd
import numpy as np
from sklearn.datasets import load_breast_cancer

from simplify import Ingredients, Inventory, Menu
from simplify.cookbook import Cookbook

# Loads cancer data and converts from numpy arrays to pandas dataframe.
cancer = load_breast_cancer()
df = pd.DataFrame(np.c_[cancer['data'], cancer['target']],
                  columns = np.append(cancer['feature_names'], ['target']))

menu = Menu(file_path = 'cancer_settings.ini')
inventory = Inventory(menu = menu, root_folder = os.path.join('..', '..'))
ingredients = Ingredients(menu = menu, inventory = inventory, df = df)
# Creates instance of Data with the cancer dataframe.
cookbook = Cookbook(menu = menu,
                    inventory = inventory,
                    ingredients = ingredients)
# Converts label to boolean type - conversion from numpy arrays leaves all
# columns as float type.
cookbook.ingredients.change_datatype(columns = ['target'], datatype = 'boolean')
# Fills missing ingredients with appropriate default values based on column
# datatype.
cookbook.ingredients.smart_fill()
# Creates instance of Cookbook.
# Iterates through every recipe and exports plots from each recipe.
cookbook.start()
# Creates and exports a table of summary statistics from the dataframe.
cookbook.ingredients.summarize()
# Saves the recipes, results, and cookbook.
cookbook.save_everything()
# Outputs information about the best recipe.
cookbook.print_best()
# Saves ingredients file.
cookbook.ingredients.save(file_name = 'cancer_df')