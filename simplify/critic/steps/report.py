
"""
.. module:: reports
:synopsis: reports for model performance
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass

from simplify.core.critic.review import CriticTechnique


@dataclass
class Report(CriticTechnique):
    """Creates reports for evaluating models.

    Args:
        technique(str): name of technique.
        parameters(dict): dictionary of parameters to pass to selected
            algorithm.
        name(str): designates the name of the class which is used throughout
            siMpLify to match methods and settings with this class and
            identically named subclasses.
        auto_publish(bool): whether 'publish' method should be called when
            the class is instanced. This should generally be set to True.

    """
    technique: object = None
    parameters: object = None
    name: str = 'reports'
    auto_publish: bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    def __str__(self):
        # """Prints to console basic results separate from report."""
        # print('These are the results using the', recipe.model.technique,
        #       'model')
        # if recipe.splicer.technique != 'none':
        #     print('Testing', recipe.splicer.technique, 'predictors')
        # print('Confusion Matrix:')
        # print(self.confusion)
        # print('Classification Report:')
        # print(self.classification_report)
        return self

    def draft(self):
        super().publish()
        self.options = {
            'classification': ['sklearn.metrics', 'classification_report'],
            'confusion': ['sklearn.metrics', 'confusion_matrix']}
        self.sequence_setting = 'report_techniques'
        return self

    def implement(self, recipe):
        self.runtime_parameters = {
            'y_true': getattr(recipe.ingredients, 'y_' + self.data_to_review),
            'y_pred': recipe.predictions}
        super().implement()
        return self

