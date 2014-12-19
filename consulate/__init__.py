"""
Consulate: A client library for Consul

"""
__version__ = '0.3.0'

from consulate.api import Session
from consulate.api import TornadoSession

# Backwards compatibility with 0.2.0
Consulate = Session
TornadoConsulate = TornadoSession
