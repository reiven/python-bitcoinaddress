"""
Copied from:
http://rosettacode.org/wiki/Bitcoin/address_validation#Python
"""
from hashlib import sha256

digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


class IllegalCharacterError(ValueError):
    """Error class for when a character is not part of base58 """


def _bytes_to_long(bytestring, byteorder):
    """For use in python version prior to 3.2 """
    result = []
    if byteorder == 'little':
        result = (v << i * 8 for (i, v) in enumerate(bytestring))
    else:
        result = (v << i * 8 for (i, v) in enumerate(reversed(bytestring)))
    return sum(result)


def _long_to_bytes(n, length, byteorder):
    """For use in python version prior to 3.2
    Source:
    http://bugs.python.org/issue16580#msg177208
    """
    if byteorder == 'little':
        indexes = range(length)
    else:
        indexes = reversed(range(length))
    return bytearray((n >> i * 8) & 0xff for i in indexes)


def decode_base58(bitcoin_address, length):
    """Decode the base58 encoded address.
    This form of base58 decoding is Bitcoin specific.
    Be careful outside of Bitcoin context.
    """
    n = 0
    for char in bitcoin_address:
        try:
            n = n * 58 + digits58.index(char)
        except:
            msg = u"Character not part of Bitcoin's base58: '%s'"
            raise IllegalCharacterError(msg % char)
    try:
        return n.to_bytes(length, 'big')
    except AttributeError:
        # Python version < 3.2
        return _long_to_bytes(n, length, 'big')


def encode_base58(bytestring):
    """Encode the bytestring to a base58 encode string. """
    # Count zero's
    zeros = 0
    for i in range(len(bytestring)):
        if bytestring[i] == 0:
            zeros += 1
        else:
            break
    try:
        n = int.from_bytes(bytestring, 'big')
    except AttributeError:
        # Python version < 3.2
        n = _bytes_to_long(bytestring, 'big')
    result = ''
    (n, rest) = divmod(n, 58)
    while n or rest:
        result += digits58[rest]
        (n, rest) = divmod(n, 58)
    return zeros * '1' + result[::-1]  # reverse string


def validate(bitcoin_address, magicbyte=False):
    """Check the integrity of the bitcoin address.

    Returns False if the address is invalid.
    >>> validate('1AGNa15ZQXAZUgFiqJ2i7Z2DPU2J6hW62i')
    True
    >>> validate('')
    False
    """
    if not magicbyte:
        magicbyte = 0
    clen = len(bitcoin_address)
    if clen < 27 or clen > 35:  # XXX or 34?
        return False
    try:
        bcbytes = decode_base58(bitcoin_address, 25)
    except IllegalCharacterError:
        return False
    if not bcbytes.startswith(chr(int(magicbyte))):
        return False
    # Compare checksum
    checksum = sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
    if bcbytes[-4:] != checksum:
        return False
    # Encoded bytestring should be equal to the original address
    # For example '14oLvT2' has a valid checksum, but is not a valid btc address
    return bitcoin_address == encode_base58(bcbytes)


if __name__ == '__main__':
    assert validate("17NdbrSGoUotzeGCcMMCqnFkEvLymoou9j")
