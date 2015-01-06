import koremutake
from werkzeug.exceptions import BadRequest


def kore_id(s):
    """
    Decode the string into an integer.
    It can be a koremutake or a decimal number.
    """
    try:
        r = koremutake.decode(s)
    except ValueError:
        r = int(s)
    return r


def coerce_to(typ, val):
    """
    Raise a BadRequest (400) exception if the value cannot be converted to the
    given type.
    Return unconverted value
    """
    try:
        typ(val)
    except ValueError:
        raise BadRequest()
    return val
