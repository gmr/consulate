KV
==
The :py:class:`KV <consulate.api.kv.KV>` class provides both high and low level access
to the Consul Key/Value service. To use the :py:class:`KV <consulate.api.kv.KV>` class,
access the :py:meth:`consulate.Consul.kv` attribute of the
:py:class:`Consul <consulate.Consul>` class.

For high-level operation, the :py:class:`KV <consulate.api.kv.KV>` class behaves
like a standard Python :py:class:`dict`. You can get, set, and delete items in
the Key/Value service just as you would with a normal dictionary.

If you need to have access to the full record associated with an item, there are
lower level methods such as :py:meth:`KV.set_record <consulate.api.kv.KV.set_record>`
and :py:meth:`KV.set_record <consulate.api.kv.KV.get_record>`. These two methods
provide access to the other fields associated with the item in Consul, including
the ``flag`` and various index related fields.

Examples of Use
---------------
Here's a big blob of example code that uses most of the functionality in the
:py:class:`KV <consul.api.kv.KV>` class. Check the comments in the code to see what
part of the class it is demonstrating.

    .. code:: python

        import consulate

        session = consulate.Consul()

        # Set the key named release_flag to True
        session.kv['release_flag'] = True

        # Get the value for the release_flag, if not set, raises AttributeError
        try:
            should_release_feature = session.kv['release_flag']
        except AttributeError:
            should_release_feature = False

        # Delete the release_flag key
        del session.kv['release_flag']

        # Fetch how many rows are set in the KV store
        print(len(self.session.kv))

        # Iterate over all keys in the kv store
        for key in session.kv:
            print('Key "{0}" set'.format(key))

        # Iterate over all key/value pairs in the kv store
        for key, value in session.kv.iteritems():
            print('{0}: {1}'.format(key, value))

        # Iterate over all keys in the kv store
        for value in session.kv.values:
            print(value)

        # Find all keys that start with "fl"
        for key in session.kv.find('fl'):
            print('Key "{0}" found'.format(key))

        # Check to see if a key called "foo" is set
        if "foo" in session.kv:
            print 'Already Set'

        # Return all of the items in the key/value store
        session.kv.items()

API
---
.. autoclass:: consulate.api.kv.KV
       :members:
       :special-members:
