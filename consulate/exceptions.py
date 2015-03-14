"""
Consulate Exceptions

"""


class ConsulateException(Exception):
    """Base Consul exception"""
    pass


class ACLDisabled(ConsulateException):
    """Raised when ACL related calls are made while ACLs are disabled"""
    pass


class ACLForbidden(ConsulateException):
    """Raised when ACLs are enabled and the token does not validate"""
    pass
