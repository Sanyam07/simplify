
from dataclasses import dataclass

from simplify.core.base import SimpleClass


@dataclass
class Review(SimpleClass):
    """Stores machine learning experiment results.

    Report creates and stores a results report and other general
    scorers/metrics for machine learning based upon the type of model used in
    the siMpLify package. Users can manually add metrics not already included
    in the metrics dictionary by passing them to Results.edit_metric.

    Attributes:
        name: a string designating the name of the class which should be
            identical to the section of the idea with relevant settings.
        auto_finalize: sets whether to automatically call the finalize method
            when the class is instanced. If you do not draft to make any
            adjustments to the options or metrics beyond the idea, this option
            should be set to True. If you draft to make such changes, finalize
            should be called when those changes are complete.
    """

    def __post_init__(self):
        super().__post_init__()  
        return self

    def _classifier_report(self):
        self.classifier_report_default = metrics.classification_report(
                self.recipe.ingredients.y_test,
                self.predictions)
        self.classifier_report_dict = metrics.classification_report(
                self.recipe.ingredients.y_test,
                self.predictions,
                output_dict = True)
        self.classifier_report = pd.DataFrame(
                self.classifier_report_dict).transpose()
        return self


    def _cluster_report(self):
        return self

    def _format_step(self, attribute):
        if getattr(self.recipe, attribute).technique in ['none', 'all']:
            step_column = getattr(self.recipe, attribute).technique
        else:
            technique = getattr(self.recipe, attribute).technique
            parameters = getattr(self.recipe, attribute).parameters
            step_column = f'{technique}, parameters = {parameters}'
        return step_column

    def _regressor_report(self):
        return self


    def _print_classifier_results(self, recipe):
        """Prints to console basic results separate from report."""
        print('These are the results using the', recipe.model.technique,
              'model')
        if recipe.splicer.technique != 'none':
            print('Testing', recipe.splicer.technique, 'predictors')
        print('Confusion Matrix:')
        print(self.confusion)
        print('Classification Report:')
        print(self.classification_report)
        return self

    def _set_columns(self):
        """Sets columns and options for report."""
        self.columns = {'recipe_number' : 'number',
                        'options' : 'techniques',
                        'seed' : 'seed',
                        'validation_set' : 'val_set'}
        for step in self.recipe.techniques:
            self.columns.update({step : step})
        self.columns_list = list(self.columns.keys())
        self.columns_list.extend(self.listify(self.metrics))
        self.report = pd.DataFrame(columns = self.columns_list)
        return self

    def draft(self):
        self.export_folder = 'experiment'
        self.export_file_name = 'review'
        self.export_file_format = self.results_format
        
    def produce(self, recipe):
        self.recipe = recipe
        if not hasattr(self, 'columns'):
            self._set_columns()
        self._create_predictions()
        self._edit_result()
        self._confusion_matrix()
        getattr(self, '_' + self.model_type + '_report')()
        return self
