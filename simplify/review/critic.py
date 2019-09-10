
from dataclasses import dataclass

from simplify.core.planner import Planner
from simplify.review.steps.evaluate import Evaluate
from simplify.review.steps.summarize import Summarize
from simplify.review.steps.visualize import Visualize


@dataclass
class Critic(Planner):

    name : str = 'review'
    auto_prepare : bool = True

    def __post_init__(self):
        super().__post_init__()
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

    def _define(self):
        """Sets default options for Recipe Review."""
        self.options = {'evaluate' : Evaluate,
                        'visualize' : Visualize,
                        'summarize' : Summarize}
        return self

    def prepare(self):
        return self

    def start(self, recipe):
        """Evaluates recipe with various tools and prepares report."""
        if self.verbose:
            print('Evaluating recipe')
        self.recipe = recipe
        if not hasattr(self, 'columns'):
            self._set_columns()
        self._create_predictions()
        self._add_result()
        self._confusion_matrix()
        getattr(self, '_' + self.model_type + '_report')()
        self._feature_summaries()
        for evaluator in self.listify(self.evaluators):
            evaluate_package = self.evaluator_options[evaluator]
            evaluate_package()
        return self


@dataclass
class Critic(SimpleClass):

    menu : object
    inventory : object
    name : str = 'critic'
    auto_prepare : bool = True

    def __post_init__(self):
        super().__post_init__()
        return self

    def _inject(self):
        self.menu.inject(instance = Review,
                         sections = ['general', 'cookbook', 'files', 'review'])
        self.menu.inject(instance = Presentation,
                         sections = ['general', 'files', 'review',
                                     'presentation'])
        return self

    def _define(self):
        self._inject()
        self.review = Review()
        self.presentation = Presentation(inventory = self.inventory)
        return self

    def prepare(self):
        self.review.prepare()
        self.presentation.prepare()
        return self

    def start(self, recipe):
        self.review.start(recipe = recipe)
        self.presentation.start(recipe = recipe, review = self.review)
        return self

        
class Report(Techinique):
    """Stores machine learning experiment results.

    Report creates and stores a results report and other general
    scorers/metrics for machine learning based upon the type of model used in
    the siMpLify package. Users can manually add metrics not already included
    in the metrics dictionary by passing them to Results.add_metric.

    Attributes:
        name: a string designating the name of the class which should be
            identical to the section of the menu with relevant settings.
        auto_prepare: sets whether to automatically call the prepare method
            when the class is instanced. If you do not plan to make any
            adjustments to the options or metrics beyond the menu, this option
            should be set to True. If you plan to make such changes, prepare
            should be called when those changes are complete.
    """

    def _check_algorithm(self, step):
        """Returns appropriate algorithm to the report attribute."""
        if step.technique in ['none', 'all']:
            return step.technique
        else:
            return step.algorithm


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
