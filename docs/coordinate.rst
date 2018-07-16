Coordinate
==========

The :py:class:`Coordinate <consulate.api.coordinate.Coordinate>` class provides
access to Consul's Network Tomography.

.. autoclass:: consulate.api.coordinate.Coordinate
       :members:
       :special-members:

Usage
-----

This code fetches the coordinates for the nodes in ``ny1`` cluster, and then
calculates the RTT between two random nodes.

.. code:: python

    import consulate

    # Create a new instance of a consulate session
    session = consulate.Consul()

    # Get coordinates for all notes in ny1 cluster
    coordinates = session.coordinate.nodes('ny1')

    # Calculate RTT between two nodes
    session.coordinate.rtt(coordinates[0], coordinates[1])
