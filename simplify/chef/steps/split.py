"""
.. module:: split
:synopsis: splits data into training, test, and/or validation sets
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

from simplify.core.technique import SimpleTechnique


@dataclass
class Split(SimpleTechnique):
    """Splits data into training, testing, and/or validation sets, uses time
    series splits, or applies k-folds cross-validation.

    Args:
        technique (str): name of technique.
        parameters (dict): dictionary of parameters to pass to selected
            algorithm.
        name (str): name of class for matching settings in the Idea instance
            and for labeling the columns in files exported by Critic.
        auto_publish (bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.
    """

    technique: object = None
    parameters: object = None
    name: str = 'split'
    auto_publish: bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    def draft(self):
        super().draft()
        self.options = {
                'group_kfold': ['sklearn.model_selection', 'GroupKFold'],
                'kfold': ['sklearn.model_selection', 'KFold'],
                'stratified': ['sklearn.model_selection', 'StratifiedKFold'],
                'time': ['sklearn.model_selection', 'TimeSeriesSplit'],
                'train_test': ['sklearn.model_selection', 'ShuffleSplit']}
        self.default_parameters = {
                'train_test': {'test_size': 0.33},
                'kfold': {'n_splits': 5, 'shuffle': False},
                'stratified': {'n_splits': 5, 'shuffle': False},
                'group_kfold': {'n_splits': 5},
                'time': {'n_splits': 5}}      
        self.extra_parameters = {'train_test': {'n_splits': 1}}
        self.selected_parameters = True
        return self
    
    def publish(self):
        self.runtime_parameters = {'random_state': self.seed}
        super().publish()
        return self
