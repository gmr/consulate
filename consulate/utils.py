import sys

PYTHON3 = True if sys.version_info > (3, 0, 0) else False


def is_string(value):
    checks = [isinstance(value, str)]
    if not PYTHON3:
        checks.append(isinstance(value, unicode))
    return any(checks)
