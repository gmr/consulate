consulate.Session
=================
The :py:class:`consulate.Session` class is core interface for interacting with
all parts of the `Consul <http://consul.io>`_ API.

Usage Examples
--------------
Here is an example where the initial :py:class:`consulate.Session` is created,
connecting to Consul at ``localhost`` on port ``8500``. Once connected, a list
of all service checks is returned.

.. code:: python

    import consulate

    # Create a new instance of a consulate session
    session = consulate.Session()

    # Get all of the service checks for the local agent
    checks = session.agent.checks()

This next example creates a new :py:class:`Session <consulate.Session>` passing
in an authorization token and then sets a key in the Consul KV service:

.. code:: python

        import consulate

        session = consulate.Session(token='5d24c96b4f6a4aefb99602ce9b60d16b')

        # Set the key named release_flag to True
        session.kv['release_flag'] = True

API
---

.. autoclass:: consulate.Session
       :members:

