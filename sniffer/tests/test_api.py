from unittest import TestCase
from ..api import file_validator, select_runnable


class SelectRunnableDecorator(TestCase):

    def test_decorator_adds_runnable_name_to_wrapped_func(self):

        def ex_validator():
            pass

        validator = select_runnable('tagged')(file_validator(ex_validator))

        self.assertEqual(validator.runnable, 'tagged')

