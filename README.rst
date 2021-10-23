Consulate: A Consul Client Library
==================================

Consulate is a Python client library and set of application for the Consul
service discovery and configuration system.

|Version| |Status| |Coverage|

Installation
------------

Consulate is available via via `pypi <https://pypi.org/project/consulate/>`_
and can be installed with easy_install or pip:

.. code:: bash

    pip install consulate

If you require communicating with Consul via a Unix socket, there is an extra
dependency that is installed via:

.. code:: bash

    pip install consulate[unixsocket]

Command Line Utilities
----------------------
Consulate comes with two command line utilities that make working with Consul
easier from a management perspective. The ``consulate`` application provides
a cli wrapper for common tasks performed.

consulate
^^^^^^^^^
The consulate application provides a CLI interface for registering a service,
backing up and restoring the contents of the KV database, and actions for getting,
setting, and deleting keys from the KV database.

.. code:: bash

    usage: consulate [-h] [--api-scheme API_SCHEME] [--api-host API_HOST]
                     [--api-port API_PORT] [--datacenter DC] [--token TOKEN]
                     {register,deregister,kv,run_once} ...

    CLI utilities for Consul

    optional arguments:
      -h, --help            show this help message and exit
      --api-scheme API_SCHEME
                            The scheme to use for connecting to Consul with
      --api-host API_HOST   The consul host to connect on
      --api-port API_PORT   The consul API port to connect to
      --datacenter DC       The datacenter to specify for the connection
      --token TOKEN         ACL token

    Commands:
      {register,deregister,kv,run_once,services}
        register            Register a service for this node
        deregister          Deregister a service for this node
        kv                  Key/Value Database Utilities
        run_once            Lock command
        services            List services for this node

    If the CONSUL_RPC_ADDR environment variable is set, it will be parsed and used
    for default values when connecting.

Service Registration Help:

.. code:: bash

    usage: consulate register [-h] [-a ADDRESS] [-p PORT] [-s SERVICE_ID]
                              [-t TAGS]
                              name {check,httpcheck,no-check,ttl} ...

    positional arguments:
      name                  The service name

    optional arguments:
      -h, --help            show this help message and exit
      -a ADDRESS, --address ADDRESS
                            Specify an address
      -p PORT, --port PORT  Specify a port
      -s SERVICE_ID, --service-id SERVICE_ID
                            Specify a service ID
      -t TAGS, --tags TAGS  Specify a comma delimited list of tags

    Service Check Options:
      {check,httpcheck,no-check,ttl}
        check               Define an external script-based check
        httpcheck           Define an HTTP-based check
        no-check            Do not enable service monitoring
        ttl                 Define a duration based TTL check

KV Database Utilities Help:

.. code:: bash

    usage: consulate kv [-h] {backup,restore,ls,mkdir,get,set,rm} ...

    optional arguments:
      -h, --help            show this help message and exit

    Key/Value Database Utilities:
      {backup,restore,ls,mkdir,get,set,rm}
        backup              Backup to stdout or a JSON file
        restore             Restore from stdin or a JSON file
        ls                  List all of the keys
        mkdir               Create a folder
        get                 Get a key from the database
        set                 Set a key in the database
        rm                  Remove a key from the database

Locking Operations Help:

.. code:: bash

    usage: consulate [-h] run_once [-i INTERVAL] prefix command

    positional arguments:
      prefix                the name of the lock which will be held in Consul.
      command               the command to run

    optional arguments:
      -h, --help            show this help message and exit
      -i, --interval        hold the lock for INTERVAL seconds

Service listing Help:

.. code:: bash

    usage: consulate services [-h] [-i INDENT]

    optional arguments:
      -h, --help            show this help message and exit
      -i INDENT, --indent INDENT
                            The indent level for output

API Usage Examples
------------------
The following examples highlight the usage of Consulate and does not document
the scope of the full Consulate API.

*Using Consulate with the Consul kv database:*

.. code:: python

    consul = consulate.Consul()

    # Set the key named release_flag to True
    consul.kv['release_flag'] = True

    # Get the value for the release_flag, if not set, raises AttributeError
    try:
        should_release_feature = consul.kv['release_flag']
    except AttributeError:
        should_release_feature = False

    # Delete the release_flag key
    del consul.kv['release_flag']

    # Find all keys that start with "fl"
    consul.kv.find('fl')

    # Find all keys that start with "feature_flag" terminated by "/" separator
    consul.kv.find('feature_flag', separator='/')

    # Check to see if a key called "foo" is set
    if "foo" in consul.kv:
        print 'Already Set'

    # Return all of the items in the key/value store
    consul.kv.items()

*Working with the Consulate.agent API:*

.. code:: python

    consul = consulate.Consul()

    # Get all of the service checks for the local agent
    checks = consul.agent.checks()

    # Get all of the services registered with the local agent
    services = consul.agent.services()

    # Add a service to the local agent
    consul.agent.service.register('redis',
                                   port=6379,
                                   tags=['master'],
                                   ttl='10s')


*Fetching health information from Consul:*

.. code:: python

    consul = consulate.Consul()

    # Get the health of a individual node
    health = consul.health.node('my-node')

    # Get all checks that are critical
    checks = consul.health.state('critical')

For more examples, check out the Consulate documentation.

.. |Version| image:: https://img.shields.io/pypi/v/consulate.svg?
   :target: https://pypi.python.org/pypi/consulate

.. |Status| image:: https://img.shields.io/travis/gmr/consulate.svg?
   :target: https://travis-ci.org/gmr/consulate

.. |Coverage| image:: https://img.shields.io/codecov/c/github/gmr/consulate.svg?
   :target: https://codecov.io/github/gmr/consulate?branch=master
