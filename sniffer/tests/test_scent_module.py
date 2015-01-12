from unittest import TestCase
from ..scent_picker import load_file
from ..scanner.base import BaseScanner


class ScentModuleTest(TestCase):

    def test_set_runner_and_get_runner_methods(self):
        scent = load_file('sniffer/tests/scent_file.py')
        self.assertEqual(scent.get_runners(), scent.runners)

        scent.set_runner('execute_type1')
        self.assertEqual(scent.get_runners(), (scent.runners[0],))

        scent.set_runner('execute_type2')
        self.assertEqual(scent.get_runners(), (scent.runners[1],))

    def test_scent_module_interaction_with_scanner(self):
        scent = load_file('sniffer/tests/scent_file.py')
        scanner = BaseScanner([], scent)

        for v in scent.validators:
            scanner.add_validator(v)

        self.assertTrue(scanner.is_valid_type('file.type1'))
        self.assertTrue(scanner.is_valid_type('file.type2'))
        self.assertFalse(scanner.is_valid_type('file.negative'))

