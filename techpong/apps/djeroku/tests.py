"""
Simple tests for djeroku
"""

from django.test import TestCase
from lib.djeroku.tools.view_tools import validate_required


class ValidateRequiredTest(TestCase):
    """Tests the validate_required function with its various inputs."""

    def test_required(self):
        success, clean = validate_required({}, {'required_field': {}})
        self.assertFalse(success)

    def test_required_custom_message(self):
        success, clean = validate_required(
                {},
                {'required_field': {}},
                {'missing_field': 'test_message'}
            )
        self.assertFalse(success)
        self.assertEqual(clean['required_field'], 'test_message')

    def test_validation(self):
        success, clean = validate_required(
                {'required_field': 'abc'},
                {'required_field': {
                        'validation': lambda a: a.isdigit()
                    }
                }
            )
        self.assertFalse(success)
        self.assertEqual(clean['required_field'], 'Validation Failed')

    def test_validation_custom_message(self):
        success, clean = validate_required(
                {'required_field': 'abc'},
                {'required_field': {
                        'validation': lambda a: a.isdigit(),
                    }
                },
                {'validation_failed': 'test_message' }
            )
        self.assertFalse(success)
        self.assertEqual(clean['required_field'], 'test_message')

    def test_validation_custom_field_message(self):
        success, clean = validate_required(
                {'required_field': 'abc'},
                {'required_field': {
                        'validation': lambda a: a.isdigit(),
                        'validation_failed_message': 'invalid field'
                    }
                },
                {'validation_failed': 'test_message' }
            )
        self.assertFalse(success)
        self.assertEqual(clean['required_field'], 'invalid field')

    def test_validation_custom_field_message_format(self):
        success, clean = validate_required(
                {'required_field': 'abc'},
                {'required_field': {
                        'validation': lambda a: a.isdigit(),
                        'validation_failed_message': 'invalid field {field}'
                    }
                },
                {'validation_failed': 'test_message' }
            )
        self.assertFalse(success)
        self.assertEqual(clean['required_field'], 'invalid field required_field')

    def test_clean(self):
        success, clean = validate_required(
                {'required_field': '123'},
                {'required_field': {
                        'validation': lambda a: a.isdigit(),
                        'clean': lambda a: int(a)
                    }
                }
            )
        self.assertTrue(success)
        self.assertEqual(clean['required_field'], 123)

    def test_clean_exception(self):
        success, clean = validate_required(
                {'required_field': '123abc'},
                {'required_field': { 'clean': lambda a: int(a) } }
            )
        self.assertFalse(success)
        self.assertEqual(clean['required_field'], 'Validation Failed')

    def test_clean_exception_custom_message(self):
        success, clean = validate_required(
                {'required_field': '123abc'},
                {'required_field': { 'clean': lambda a: int(a) } },
                {'clean_failed': 'test_message'}
            )
        self.assertFalse(success)
        self.assertEqual(clean['required_field'], 'test_message')

    def test_clean_exception_custom_field_message(self):
        success, clean = validate_required(
                {'required_field': '123abc'},
                {'required_field': {
                        'clean': lambda a: int(a),
                        'clean_failed_message': 'uncleanable'
                    }
                },
                {'clean_failed': 'test_message'}
            )
        self.assertFalse(success)
        self.assertEqual(clean['required_field'], 'uncleanable')

    def test_clean_exception_custom_field_message_format(self):
        success, clean = validate_required(
                {'required_field': '123abc'},
                {'required_field': {
                        'clean': lambda a: int(a),
                        'clean_failed_message': '{field} is bad'
                    }
                },
                {'clean_failed': 'test_message'}
            )
        self.assertFalse(success)
        self.assertEqual(clean['required_field'], 'required_field is bad')

    def test_return_only_failures(self):
        success, clean = validate_required(
                {'required_field': 'abc', 'other_field': '123'},
                {
                    'required_field': {
                        'validation': lambda a: a.isdigit(),
                        'validation_failed_message': 'invalid field {field}'
                    },
                    'other_field': {}
                }
            )
        self.assertFalse(success)
        self.assertEqual(clean['required_field'], 'invalid field required_field')
        self.assertFalse('other_field' in clean)

    def test_multi_field(self):
        success, clean = validate_required(
                {'required_field': 'abc', 'other_field': '123'},
                {
                    'required_field': {
                        'validation': lambda a: a.isalnum(),
                        'validation_failed_message': 'invalid field {field}',
                        'clean': lambda a: a.upper()
                    },
                    'other_field': {
                        'validation': lambda a: a.isdigit(),
                        'clean': lambda a: int(a)
                    }
                }
            )
        self.assertTrue(success)
        self.assertEqual(clean['required_field'], 'ABC')
        self.assertEqual(clean['other_field'], 123)

