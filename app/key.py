from random import choice
from string import ascii_uppercase
from string import digits


def generate_key(n):
    return ''.join(choice(ascii_uppercase + digits) for x in range(n))


def get_secret_key(filename):
    try:
        with open(filename) as f:
            secret = f.read()
    except IOError as e:
        secret = generate_key(64)
        with open(filename, 'w+') as f:
            f.write(secret)
    return secret
