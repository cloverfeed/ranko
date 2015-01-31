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
