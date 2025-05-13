from django.test import TestCase
from validator.enums import ValidationType


class ValidationTypeTest(TestCase):
    def test_validation_type_values(self):
        self.assertEqual(ValidationType.NORMAL.value, 'normal')
        self.assertEqual(ValidationType.FALSE.value, 'false')
        self.assertEqual(ValidationType.ROOT.value, 'root')
        self.assertEqual(ValidationType.ROOT_TYPE.value, 'root_type') 