"""
Consul KV Endpoint Access

"""
from consulate.api import base
from consulate import utils


class KV(base.Endpoint):
    """The :py:class:`consul.api.KV` class implements a :py:class:`dict` like
    interface for working with the Key/Value service. Simply use items on the
    :py:class:`consulate.Session` like you would with a :py:class:`dict` to
    :py:meth:`get <consulate.api.KV.get>`,
    :py:meth:`set <consulate.api.KV.set>`, or
    :py:meth:`delete <consulate.api.KV.delete>` values in the key/value store.

    Additionally, :py:class:`KV <consulate.api.KV>` acts as an
    :py:meth:`iterator <consulate.api.KV.__iter__>`, providing methods to
    iterate over :py:meth:`keys <consulate.api.KV.keys>`,
    :py:meth:`values <consulate.api.KV.values>`,
    :py:meth:`keys and values <consulate.api.KV.iteritems>`, etc.

    Should you need access to get or set the flag value, the
    :py:meth:`get_record <consulate.api.KV.get_record>`,
    :py:meth:`set_record <consulate.api.KV.set_record>`,
    and :py:meth:`records <consulate.api.KV.records>` provide a way to access
    the additional fields exposed by the KV service.

    """

    def __contains__(self, item):
        """Return True if there is a value set in the Key/Value service for the
        given key.

        :param str item: The key to check for
        :rtype: bool

        """
        item = item.lstrip('/')
        return self._get_no_response_body([item])

    def __delitem__(self, item):
        """Delete an item from the Key/Value service

        :param str item: The key name

        """
        self._delete_item(item)

    def __getitem__(self, item):
        """Get a value from the Key/Value service, returning it fully
        decoded if possible.

        :param str item: The item name
        :rtype: mixed
        :raises: KeyError

        """
        value = self._get_item(item)
        if not value:
            raise KeyError('Key not found ({0})'.format(item))
        return value.get('Value')

    def __iter__(self):
        """Iterate over all the keys in the Key/Value service

        :rtype: iterator

        """
        for key in self.keys():
            yield key

    def __len__(self):
        """Return the number if items in the Key/Value service

        :return: int

        """
        return len(self._get_all_items())

    def __setitem__(self, item, value):
        """Set a value in the Key/Value service, using the CAS mechanism
        to ensure that the set is atomic. If the value passed in is not a
        string, an attempt will be made to JSON encode the value prior to
        setting it.

        :param str item: The key to set
        :param mixed value: The value to set
        :raises: KeyError

        """
        self._set_item(item, value)

    def acquire_lock(self, item, session):
        """Use Consul for locking by specifying the item/key to lock with
        and a session value for removing the lock.

        :param str item: The item in the Consul KV database
        :param str session: The session value for the lock
        :return: bool

        """
        return self._put_response_body([item], {'acquire': session})

    def delete(self, item, recurse=False):
        """Delete an item from the Key/Value service

        :param str item: The item key
        :param bool recurse: Remove keys prefixed with the item pattern
        :raises: KeyError

        """
        return self._delete_item(item, recurse)

    def get(self, item, default=None, raw=False):
        """Get a value from the Key/Value service, returning it fully
        decoded if possible.

        :param str item: The item key
        :rtype: mixed
        :raises: KeyError

        """
        response = self._get_item(item, raw)
        if isinstance(response, dict):
            return response.get('Value', default)
        return response or default

    def get_record(self, item):
        """Get the full record from the Key/Value service, returning
        all fields including the flag.

        :param str item: The item key
        :rtype: dict
        :raises: KeyError

        """
        return self._get_item(item)

    def find(self, prefix, separator=None):
        """Find all keys with the specified prefix, returning a dict of
        matches.

        *Example:*

        .. code:: python

            >>> consul.kv.find('b')
            {'baz': 'qux', 'bar': 'baz'}

        :param str prefix: The prefix to search with
        :rtype: dict

        """
        query_params = {'recurse': None}
        if separator:
            query_params['keys'] = prefix
            query_params['separator'] = separator
        response = self._get_list([prefix.lstrip('/')], query_params)
        if separator:
            results = response
        else:
            results = {}
            for row in response:
                results[row['Key']] = row['Value']
        return results

    def items(self):
        """Return a dict of all of the key/value pairs in the Key/Value service

        *Example:*

        .. code:: python

            >>> consul.kv.items()
            {'foo': 'bar', 'bar': 'baz', 'quz': True, 'corgie': 'dog'}

       :rtype: dict

        """
        return [{item['Key']: item['Value']} for item in self._get_all_items()]

    def iteritems(self):
        """Iterate over the dict of key/value pairs in the Key/Value service

        *Example:*

        .. code:: python

            >>> for key, value in consul.kv.iteritems():
            ...     print(key, value)
            ...
            (u'bar', 'baz')
            (u'foo', 'bar')
            (u'quz', True)

       :rtype: iterator

        """
        for item in self._get_all_items():
            yield item['Key'], item['Value']

    def keys(self):
        """Return a list of all of the keys in the Key/Value service

        *Example:*

        .. code:: python

            >>> consul.kv.keys()
            [u'bar', u'foo', u'quz']

        :rtype: list

        """
        return sorted([row['Key'] for row in self._get_all_items()])

    def records(self):
        """Return a list of tuples for all of the records in the Key/Value
        service

        *Example:*

        .. code:: python

            >>> consul.kv.records()
            [(u'bar', 0, 'baz'),
             (u'corgie', 128, 'dog'),
             (u'foo', 0, 'bar'),
             (u'quz', 0, True)]

        :rtype: list of (Key, Flags, Value)

        """
        return [(item['Key'], item['Flags'], item['Value'])
                for item in self._get_all_items()]

    def release_lock(self, item, session):
        """Release an existing lock from the Consul KV database.

        :param str item: The item in the Consul KV database
        :param str session: The session value for the lock
        :return: bool

        """
        return self._put_response_body([item], {'release': session})

    def set(self, item, value):
        """Set a value in the Key/Value service, using the CAS mechanism
        to ensure that the set is atomic. If the value passed in is not a
        string, an attempt will be made to JSON encode the value prior to
        setting it.

        :param str item: The key to set
        :param mixed value: The value to set
        :raises: KeyError

        """
        return self.__setitem__(item, value)

    def set_record(self, item, flags=0, value=None, replace=True):
        """Set a full record, including the item flag

        :param str item: The key to set
        :param mixed value: The value to set
        :param replace: If True existing value will be overwritten:

        """
        self._set_item(item, value, flags, replace)

    def values(self):
        """Return a list of all of the values in the Key/Value service

        *Example:*

        .. code:: python

            >>> consul.kv.values()
            [True, 'bar', 'baz']

        :rtype: list

        """
        return [row['Value'] for row in self._get_all_items()]

    def _delete_item(self, item, recurse=False):
        """Remove an item from the Consul database

        :param str item:
        :param recurse:
        :return:
        """
        query_params = {'recurse': True} if recurse else {}
        return self._adapter.delete(self._build_uri([item], query_params))

    def _get_all_items(self):
        """Internal method to return a list of all items in the Key/Value
        service

        :rtype: list

        """
        return self._get_list([''], {'recurse': None})

    def _get_item(self, item, raw=False):
        """Internal method to get the full item record from the Key/Value
        service

        :param str item: The item to get
        :param bool raw: Return only the raw body
        :rtype: mixed

        """
        item = item.lstrip('/')
        query_params = {'raw': True} if raw else {}
        response = self._adapter.get(self._build_uri([item], query_params))
        if response.status_code == 200:
            return response.body
        return None

    def _get_modify_index(self, item, value, replace):
        """Get the modify index of the specified item. If replace is False
        and an item is found, return ``None``. If the existing value
        and the passed in value match, return ``None``. If no item exists in
        the KV database, return ``0``, otherwise return the ``ModifyIndex``.

        :param str item: The item to get the index for
        :param str value: The item to evaluate for equality
        :param bool replace: Should the item be replaced
        :rtype: int|None

        """
        response = self._adapter.get(self._build_uri([item]))
        index = 0
        if response.status_code == 200:
            index = response.body.get('ModifyIndex')
            rvalue = response.body.get('Value')
            if rvalue == value:
                return None
            if not replace:
                return None
        return index

    @staticmethod
    def _prepare_value(value):
        """Prepare the value passed in and ensure that it is properly encoded

        :param mixed value: The value to prepare
        :rtype: bytes

        """
        if not utils.is_string(value) or isinstance(value, bytes):
            return value
        try:
            if utils.PYTHON3:
                return value.encode('utf-8')
            elif isinstance(value, unicode):
                return value.encode('utf-8')
        except UnicodeDecodeError:
            return value
        return value

    def _set_item(self, item, value, flags=None, replace=True):
        """Internal method for setting a key/value pair with flags in the
        Key/Value service

        :param str item: The key to set
        :param mixed value: The value to set
        :param int flags: User defined flags to set
        :param bool replace: Overwrite existing values
        :raises: KeyError

        """
        value = self._prepare_value(value)
        if value and item.endswith('/'):
            item = item.rstrip('/')

        index = self._get_modify_index(item, value, replace)
        if index is None:
            return True

        query_params = {'cas': index}
        if flags is not None:
            query_params['flags'] = flags
        response = self._adapter.put(self._build_uri([item], query_params),
                                     value)
        if not response.status_code == 200 or not response.body:
            raise KeyError(
                'Error setting "{0}" ({1})'.format(item, response.status_code))
