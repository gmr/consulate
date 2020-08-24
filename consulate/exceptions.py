"""
Consulate Exceptions

"""


class ConsulateException(Exception):
    """Base Consul exception"""


class RequestError(ConsulateException):
    """There was an error making the request to the consul server"""


class ClientError(ConsulateException):
    """There was an error in the request that was made to consul"""


class ServerError(ConsulateException):
    """An internal Consul server error occurred"""


class ACLDisabled(ConsulateException):
    """Raised when ACL related calls are made while ACLs are disabled"""


class ACLFormatError(ConsulateException):
    """Raised when PolicyLinks is missing 'ID' and 'Name' in a PolicyLink or
    when ServiceIdentities is missing 'ServiceName' field in a ServiceIdentity.

    """


class Forbidden(ConsulateException):
    """Raised when ACLs are enabled and the token does not validate"""


class NotFound(ConsulateException):
    """Raised when an operation is attempted with a value that can not be
    found.

    """


class LockFailure(ConsulateException):
    """Raised by :class:`~consulate.api.lock.Lock` if the lock can not be
    acquired.

    """
