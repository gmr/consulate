Consulate: A Consul Client Library
==================================

Consulate is a Python client library and set of application for the Consul
service discovery and configuration system.

|Version| |Downloads| |License| |Build Status|

Installation
------------

Consulate is available via via `pypi <https://pypi.python.org/pypi/consulate>`_
and can be installed with easy_install or pip:

.. code:: bash

    pip install consulate

Command Line Utilities
----------------------
Consulate comes with two command line utilities that make working with Consul
easier from a management perspective. The ``consulate`` application provides
a cli wrapper for common tasks performed.

The ``passport`` application has been moved to a stand-alone application and
is available at https://github.com/gmr/passport.

consulate
^^^^^^^^^
The consulate application provides a CLI interface for registering a service,
backing up and restoring the contents of the KV database, and actions for getting,
setting, and deleting keys from the KV database.

.. code:: bash

    usage: consulate [-h] [--api-host API_HOST] [--api-port API_PORT]
                     [--datacenter DATACENTER]
                     {register,kv} ...

    optional arguments:
      -h, --help            show this help message and exit
      --api-host API_HOST   The consul host to connect on
      --api-port API_PORT   The consul API port to connect to
      --datacenter DATACENTER
                            The datacenter to specify for the connection

    Commands:
      {register,kv}
        register            Register a service for this node
        kv                  Key/Value Database Utilities

Service Registration Help:

.. code:: bash

    usage: consulate register [-h] [-s SERVICE_ID] [-t TAGS]
                              {check,no-check,ttl} ... name port

    positional arguments:
      name                  The service name
      port                  The port the service runs on

    optional arguments:
      -h, --help            show this help message and exit
      -s SERVICE_ID, --service-id SERVICE_ID
                            Specify a service ID
      -t TAGS, --tags TAGS  Specify a comma delimited list of tags

    Service Check Options:
      {check,no-check,ttl}
        check               Define an external script-based check
        no-check            Do not enable service monitoring
        ttl                 Define a duration based TTL check

KV Database Utilities Help:

.. code:: bash

    usage: consulate kv [-h] {backup,restore,get,set,del} ...

    optional arguments:
      -h, --help            show this help message and exit

    Key/Value Database Utilities:
      {backup,restore,get,set,del}
        backup              Backup to a JSON file
        restore             Restore from a JSON file
        get                 Get a key from the database
        set                 Set a key in the database
        del                 Delete a key from the database

API Usage Examples
------------------
The following examples highlight the usage of Consulate and does not document
the scope of the full Consulate API.

*Using Consulate with the Consul kv database:*

.. code:: python

    session = consulate.Consulate()

    # Set the key named release_flag to True
    session.kv['release_flag'] = True

    # Get the value for the release_flag, if not set, raises AttributeError
    try:
        should_release_feature = session.kv['release_flag']
    except AttributeError:
        should_release_feature = False

    # Delete the release_flag key
    del session.kv['release_flag']

    # Find all keys that start with "fl"
    session.kv.find('fl')

    # Find all keys that start with "feature_flag" terminated by "/" separator
    session.kv.find('feature_flag', separator='/')

    # Check to see if a key called "foo" is set
    if "foo" in session.kv:
        print 'Already Set'

    # Return all of the items in the key/value store
    session.kv.items()

*Working with the Consulate.agent API:*

.. code:: python

    session = consulate.Consulate()

    # Get all of the service checks for the local agent
    checks = session.agent.checks()

    # Get all of the services registered with the local agent
    services = session.agent.services()

    # Add a service to the local agent
    session.agent.service.register('redis',
                                   port=6379,
                                   tags=['master'],
                                   ttl='10s')


*Fetching health information from Consul:*

.. code:: python

    session = consulate.Consulate()

    # Get the health of a individual node
    health = session.health.node('my-node')

    # Get all checks that are critical
    checks = session.heath.state('critical')

For more examples, check out the Consulate documentation.

.. |Version| image:: https://badge.fury.io/py/consulate.svg?
   :target: http://badge.fury.io/py/consulate

.. |Downloads| image:: https://pypip.in/d/consulate/badge.svg?
   :target: https://pypi.python.org/pypi/consulate

.. |License| image:: https://pypip.in/license/consulate/badge.svg?
   :target: https://consulate.readthedocs.org

.. |Build Status| image:: https://travis-ci.org/gmr/consulate.svg?branch=master
    :target: https://travis-ci.org/gmr/consulate
