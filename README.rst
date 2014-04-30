Consulate: A Consul Client Library
==================================
Consulate is a Python API for the Consul service discovery and configuration
system.

------------
Installation
------------
Consulate is available via pypi_ and can be installed with easy_install or pip:

.. code:: bash

    pip install consulate

-------------
Consulate API
-------------
Consul is accessed via the ``consulate.Consulate`` class which exposes several
objects for interacting with the local Consul agent.

kv
==
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

Consulate.kv.items()
''''''''''''''''''''
Return all key/value pairs in the Consul kv database.

**Return Values**
``dict``
    Key/Value pairs found

agent
=====
Provides API methods for working with nodes, services and checks via the agent.










.. _pypi: https://pypi.python.org/pypi/consulate
