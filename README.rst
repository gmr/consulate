==================================
Consulate: A Consul Client Library
==================================

Consulate is a Python API for the Consul service discovery and configuration
system.

|Version| |Downloads| |Status| |Coverage| |License|

Installation
------------

Consulate is available via pypi_ and can be installed with easy_install or pip:

.. code:: bash

    pip install consulate

Documentation
-------------
Documentation is available at https://consulate.readthedocs.org

Usage Examples
--------------
The following examples highlight the usage of Consulate and does not document
the scope of the full Consulate API.

`Using Consulate with the Consul kv database:`

.. code :: python

    session = consulate.Consulate()

    # Set the key named release_flag to True
    session.kv.release_flag = True

    # Get the value for the release_flag, if not set, raises AttributeError
    try:
        should_release_feature = session.kv.release_flag
    except AttributeError:
        should_release_feature = False

    # Delete the release_flag key
    del session.kv.release_flag

    # Find all keys that start with "fl"
    session.kv.find('fl')

    # Check to see if a key called "foo" is set
    if "foo" in session.kv:
        print 'Already Set'

    # Return all of the items in the key/value store
    session.kv.items()

`Working with the Consulate.agent API:`

.. code :: python

    session = consulate.Consulate()

    # Get all of the service checks for the local agent
    checks = session.agent.checks()

    # Get all of the services registered with the local agent
    services = session.agent.services()

    # Add a service to the local agent
    session.agent.service.register('redis',
                                   port=6379,
                                   tags=['master'],
                                   check={'script': None,
                                          'interval': None,
                                          'ttl': '60s')


`Fetching health information from Consul:`

.. code :: python

    session = consulate.Consulate()

    # Get the health of a individual node
    health = session.health.node('my-node')

    # Get all checks that are critical
    checks = session.heath.state('critical')

For more examples, check out the Consulate documentation.

.. |Version| image:: https://badge.fury.io/py/consulate.svg?
   :target: http://badge.fury.io/py/consulate

.. |Status| image:: https://travis-ci.org/gmr/consulate.svg?branch=master
   :target: https://travis-ci.org/gmr/consulate

.. |Coverage| image:: https://coveralls.io/repos/gmr/consulate/badge.png
   :target: https://coveralls.io/r/gmr/consulate
  
.. |Downloads| image:: https://pypip.in/d/consulate/badge.svg?
   :target: https://pypi.python.org/pypi/consulate
   
.. |License| image:: https://pypip.in/license/consulate/badge.svg?
   :target: https://consulate.readthedocs.org
