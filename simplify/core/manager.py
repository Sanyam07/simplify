"""
.. module:: manager
:synopsis: builder of siMpLify iterable plans
:author: Corey Rayburn Yung
:copyright: 2019
:license: Apache-2.0
"""

from dataclasses import dataclass
from itertools import product

from simplify.core.base import SimpleClass


@dataclass
class SimpleManager(SimpleClass):
    """Parent class for siMpLify planners like Cookbook, Almanac, Analysis,
    and Canvas.

    This class adds methods useful to create iterators, iterate over user
    options, and transform data or fit models.

    It is also a child class of SimpleClass. So, its documentation applies as
    well.
    """

    def __post_init__(self):
        super().__post_init__()
        return self

    """ Private Methods """
            
    def _create_steps_lists(self):
        """Creates list of lists of all possible step lists corresponding to the
        keys in 'options'."""
        self.all_steps = []
        for step in self.options.keys():
            # Stores each step attribute in a list.
            if hasattr(self, step):
                setattr(self, step, self.listify(getattr(self, step)))
            # Stores a list of 'none' if there is no corresponding local
            # attribute.
            else:
                setattr(self, step, ['none'])
            # Adds step to a list of all steps.
            self.all_steps.append(getattr(self, step))
        return self

    def _get_return_variables(self, instance, return_variables = None):
        """Adds 'return_variables' attributes from instance class to present 
        class.
        
        Args:
            instance(object): class instance with attributes to be added to the
                present subclass.
            return_variables(list(str) or str): names of attributes sought.
        
        """
        if return_variables is None and self.exists('return_variables'):
            return_variables = self.return_variables
        if return_variables is not None:
            for variable in self.listify(return_variables):
                if hasattr(instance, variable):
                    setattr(self, variable, getattr(instance, variable))
        return self

    def _publish_parallel(self):
        """Creates iterable from list of lists in 'all_steps'."""
        # Creates a list of all possible permutations of step lists.
        all_plans = list(map(list, product(*self.all_steps)))
        for i, plan in enumerate(all_plans):
            published_steps = {}
            for j, (step_name, step_class) in enumerate(self.options.items()):
                published_steps.update(
                        {step_name: step_class(technique = plan[j])})
            getattr(self, self.iterable).update(
                    {i + 1: self.iterable_class(steps = published_steps,
                                                number = i + 1)})
        return self

    def _publish_serial(self):
        """Creates iterable from list of lists in 'all_steps'."""
        for i, (name, iterable_class) in enumerate(self.options.items()):
            for steps in self.all_steps[i]:
                getattr(self, self.iterable).update(
                        {i + 1: iterable_class(steps = steps)})
        return self

    """ Core siMpLify methods """

    def draft(self):
        """ Declares defaults for class."""
        super().draft()
        self.checks.extend(['steps', 'depot', 'iterable'])
        self.state_attributes = ['depot', 'ingredients']
        return self

    def publish(self):
        """Finalizes iterable dictionary of steps with instanced step 
        classes."""
        self._create_steps_lists()
        getattr(self, '_publish_' + self.iterable_type)()
        return self

    def implement(self, *args, **kwargs):
        """Method that implements all of the publishd objects with the passed
        args and kwargs.
        
        If 'return_variables' is defined. Those named attributes are copied from
        step class instances to the present class.

        Args:
            *args, **kwargs: other parameters can be added to method as needed.
            
        """
        for number, step in getattr(self, self.iterable).items():
            if self.verbose and self.iterable_type in ['parallel']:
                print('Testing', self.name, str(number))
            elif self.verbose and self.iterable_type in ['serial']:
                print('Applying', self.name, 'methods')
            step.implement(*args, **kwargs)
            if self.exists('return_variables'): 
                self._get_return_variables(instance = step)
        return self