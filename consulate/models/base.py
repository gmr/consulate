# coding=utf-8
"""
Base Model

"""
import collections


class Model(collections.Iterable):
    """A model contains an __attribute__ map that defines the name,
    its type for type validation, an optional validation method, a method
    used to

    .. python::

        class MyModel(Model):

            __attributes__ = {
                'ID': {
                    'type': uuid.UUID,
                    'required': False,
                    'default': None,
                    'cast_from': str,
                    'cast_to': str
                },
                'Serial': {
                    'type': int
                    'required': True,
                    'default': 0,
                    'validator': lambda v: v >= 0 end,
                }
            }

    """

    __attributes__ = {}
    """The attributes that define the data elements of the model"""

    def __init__(self, **kwargs):
        super(Model, self).__init__()
        [setattr(self, name, value) for name, value in kwargs.items()]
        [self._set_default(name) for name in self.__attributes__.keys()
         if name not in kwargs.keys()]

    def __iter__(self):
        """Iterate through the model's key, value pairs.

        :rtype: iterator

        """
        for name in self.__attributes__.keys():
            value = self._maybe_cast_value(name)
            if value is not None:
                yield self._maybe_return_key(name), value

    def __setattr__(self, name, value):
        """Set the value for an attribute of the model, validating the
        attribute name and its type if the type is defined in ``__types__``.

        :param str name: The attribute name
        :param mixed value: The value to set
        :raises: AttributeError
        :raises: TypeError
        :raises: ValueError

        """
        if name not in self.__attributes__:
            raise AttributeError('Invalid attribute "{}"'.format(name))
        value = self._validate_value(name, value)
        super(Model, self).__setattr__(name, value)

    def __getattribute__(self, name):
        """Return the attribute from the model if it is set, otherwise
        returning the default if one is set.

        :param str name: The attribute name
        :rtype: mixed

        """
        try:
            return super(Model, self).__getattribute__(name)
        except AttributeError:
            if name in self.__attributes__:
                return self.__attributes__[name].get('default', None)
            raise

    def _maybe_cast_value(self, name):
        """Return the attribute value, possibly cast to a different type if
        the ``cast_to`` item is set in the attribute definition.

        :param str name: The attribute name
        :rtype: mixed

        """
        value = getattr(self, name)
        if value is not None and self.__attributes__[name].get('cast_to'):
            return self.__attributes__[name]['cast_to'](value)
        return value

    def _maybe_return_key(self, name):
        """Return the attribute name as specified in it's ``key`` definition,
        if specified. This is to map python attribute names to their Consul
        alternatives.

        :param str name: The attribute name
        :rtype: mixed

        """
        if self.__attributes__[name].get('key'):
            return self.__attributes__[name]['key']
        return name

    def _required_attr(self, name):
        """Returns :data:`True` if the attribute is required.

        :param str name: The attribute name
        :rtype: bool

        """
        return self.__attributes__[name].get('required', False)

    def _set_default(self, name):
        """Set the default value for the attribute name.

        :param str name: The attribute name

        """
        setattr(self, name, self.__attributes__[name].get('default', None))

    def _validate_value(self, name, value):
        """Ensures the the value validates based upon the type or a validation
        function, raising an error if it does not.

        :param str name: The attribute name
        :param mixed value: The value that is being set
        :rtype: mixed
        :raises: TypeError
        :raises: ValueError

        """
        if value is None:
            if self._required_attr(name):
                raise ValueError('Attribute "{}" is required'.format(name))
            return

        if not isinstance(value, self.__attributes__[name].get('type')):
            cast_from = self.__attributes__[name].get('cast_from')
            if cast_from and isinstance(value, cast_from):
                value = self.__attributes__[name]['type'](value)
            else:
                raise TypeError(
                    'Attribute "{}" must be of type {} not {}'.format(
                        name, self.__attributes__[name]['type'].__name__,
                        value.__class__.__name__))

        if self.__attributes__[name].get('enum') \
                and value not in self.__attributes__[name]['enum']:
            raise ValueError(
                'Attribute "{}" value {!r} not valid'.format(name, value))

        validator = self.__attributes__[name].get('validator')
        if callable(validator):
            if not validator(value, self):
                raise ValueError(
                    'Attribute "{}" value {!r} did not validate'.format(
                        name, value))
        return value
