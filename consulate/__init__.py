"""
Consulate: A client library for Consul

"""
__version__ = '0.4.0'

from consulate.api import Consul

# Backwards compatibility with 0.3.0
Session = Consul

import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """Python 2.6 does not have a NullHandler"""
        def emit(self, record):
            """Emit a record
            :param record record: The record to emit
            """
            pass

logging.getLogger('consulate').addHandler(NullHandler())
