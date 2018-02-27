# coding=utf-8
"""Tests for the Base Model"""
import unittest
import uuid

from consulate.models import base


class TestModel(base.Model):
    """Model to perform tests against"""
    __slots__ = ['id', 'serial', 'name', 'value']
    __attributes__ = {
        'id': {
            'key': 'ID',
            'type': uuid.UUID,
            'cast_from': str,
            'cast_to': str,
        },
        'serial': {
            'key': 'Serial',
            'type': int,
            'default': 0,
            'required': True,
            'validator': lambda v: v >= 0,
        },
        'name': {
            'key': 'Name',
            'type': str,
            'required': True
        },
        'value': {
            'type': str
        },
        'type': {
            'key': 'Type',
            'type': str,
            'enum': {'client', 'server'}
        }
    }


class TestCase(unittest.TestCase):

    def test_happy_case_with_defaults(self):
        kwargs = {
            'id': uuid.uuid4(),
            'name': str(uuid.uuid4())
        }
        model = TestModel(**kwargs)
        for key, value in kwargs.items():
            self.assertEqual(getattr(model, key), value)
        self.assertEqual(model.serial, 0)

    def test_happy_case_with_all_values(self):
        kwargs = {
            'id': uuid.uuid4(),
            'serial': 1,
            'name': str(uuid.uuid4()),
            'value': str(uuid.uuid4())
        }
        model = TestModel(**kwargs)
        for key, value in kwargs.items():
            self.assertEqual(getattr(model, key), value)

    def test_cast_from_str(self):
        expectation = uuid.uuid4()
        kwargs = {
            'id': str(expectation),
            'name': str(uuid.uuid4())
        }
        model = TestModel(**kwargs)
        self.assertEqual(model.id, expectation)

    def test_validator_failure(self):
        kwargs = {
            'id': uuid.uuid4(),
            'name': str(uuid.uuid4()),
            'serial': -1
        }
        with self.assertRaises(ValueError):
            TestModel(**kwargs)

    def test_type_failure(self):
        kwargs = {
            'id': True,
            'name': str(uuid.uuid4())
        }
        with self.assertRaises(TypeError):
            TestModel(**kwargs)

    def test_missing_requirement(self):
        with self.assertRaises(ValueError):
            TestModel()

    def test_invalid_attribute(self):
        kwargs = {'name': str(uuid.uuid4()), 'foo': 'bar'}
        with self.assertRaises(AttributeError):
            TestModel(**kwargs)

    def test_invalid_attribute_assignment(self):
        kwargs = {'name': str(uuid.uuid4())}
        model = TestModel(**kwargs)
        with self.assertRaises(AttributeError):
            model.foo = 'bar'

    def test_invalid_enum_assignment(self):
        kwargs = {'name': str(uuid.uuid4()), 'type': 'invalid'}
        with self.assertRaises(ValueError):
            TestModel(**kwargs)

    def test_cast_to_dict(self):
        kwargs = {
            'id': uuid.uuid4(),
            'serial': 1,
            'name': str(uuid.uuid4()),
            'value': str(uuid.uuid4()),
            'type': 'client'
        }
        expectation = {
            'ID': str(kwargs['id']),
            'Serial': kwargs['serial'],
            'Name': kwargs['name'],
            'value': kwargs['value'],
            'Type': kwargs['type']
        }
        model = TestModel(**kwargs)
        self.assertDictEqual(dict(model), expectation)

    def test_cast_to_dict_only_requirements(self):
        kwargs = {
            'serial': 1,
            'name': str(uuid.uuid4())
        }
        expectation = {
            'Serial': kwargs['serial'],
            'Name': kwargs['name']
        }
        model = TestModel(**kwargs)
        self.assertDictEqual(dict(model), expectation)
