Consul
======
The :py:class:`consulate.Consul` class is core interface for interacting with
all parts of the `Consul <http://consul.io>`_ API.

Usage Examples
--------------
Here is an example where the initial :py:class:`consulate.Consul` is created,
connecting to Consul at ``localhost`` on port ``8500``. Once connected, a list
of all service checks is returned.

.. code:: python

    import consulate

    # Create a new instance of a consulate session
    session = consulate.Consul()

    # Get all of the service checks for the local agent
    checks = session.agent.checks()

This next example creates a new :py:class:`Consul <consulate.Consul>` passing
in an authorization token and then sets a key in the Consul KV service:

.. code:: python

        import consulate

        session = consulate.Consul(token='5d24c96b4f6a4aefb99602ce9b60d16b')

        # Set the key named release_flag to True
        session.kv['release_flag'] = True

API
---

.. autoclass:: consulate.Consul
       :members:

