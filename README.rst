Consulate: A Consul Client Library
==================================

Installation
------------


Consulate API
-------------
Consul is accessed via the ``consulate.Consulate`` class which exposes several
objects for interacting with the local Consul agent.

kv
``
Set key/value pairs in the Consul kv database by getting, setting and deleting
attributes on ``Consulate.kv`` object. Additionally, there are methods for
finding values in the database as well as returning all key/value pairs.

Consulate.kv.find(``pattern``)
''''''''''''''''''''''''''''''
Find all keys with the specified prefix, returning a dict of key/value matches.

**Parameters**
pattern (``str``)
    Base string to search for

**Return Values**
``dict``
    Key/Value pairs found


