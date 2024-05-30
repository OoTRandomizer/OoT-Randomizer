# Author: BlackoutRoulette
# License: MIT
# Source: https://github.com/blackoutroulette/PyBase32k
import re

BITS_PER_CHAR = 15  # Base32768 is a 15-bit encoding
BITS_PER_BYTE = 8

PAIR_STR = [
    'ҠҿԀԟڀڿݠޟ߀ߟကဟႠႿᄀᅟᆀᆟᇠሿበቿዠዿጠጿᎠᏟᐠᙟᚠᛟកសᠠᡟᣀᣟᦀᦟ᧠᧿ᨠᨿᯀᯟᰀᰟᴀᴟ⇠⇿⋀⋟⍀⏟␀␟─❟➀➿⠀⥿⦠⦿⨠⩟⪀⪿⫠⭟ⰀⰟⲀⳟⴀⴟⵀⵟ⺠⻟㇀㇟㐀䶟䷀龿ꀀꑿ꒠꒿ꔀꗿꙀꙟꚠꛟ꜀ꝟꞀꞟꡀꡟ',
    'ƀƟɀʟ'
]

_LOOKUP_ENC = {}
_LOOKUP_DEC = {}


def _build_lookup():
    for i, s in enumerate(PAIR_STR):
        match = list(re.findall("..", s))
        encode_repertoire = [chr(cp) for pair in match for cp in range(ord(pair[0]), ord(pair[1]) + 1)]

        num_z_bits = BITS_PER_CHAR - BITS_PER_BYTE * i  # 0 -> 15, 1 -> 7
        _LOOKUP_ENC[num_z_bits] = encode_repertoire
        for z, c in enumerate(encode_repertoire):
            _LOOKUP_DEC[c] = (num_z_bits, z)


_build_lookup()


def encode(bytes_: bytes) -> str:
    """
    Encodes a bytes object into a Base32768 string.
    :param bytes_: a bytes object
    :return: the encoded Base32768 string
    """
    if type(bytes_) is not bytes:
        raise TypeError('Argument must be bytes')

    s: str = ''
    z: int = 0
    num_z_bits: int = 0

    for byte in bytes_:
        # Take most significant bit first
        for j in range(BITS_PER_BYTE - 1, -1, -1):
            bit: int = (byte >> j) & 1

            z = (z << 1) + bit
            num_z_bits += 1

            if num_z_bits == BITS_PER_CHAR:
                s += _LOOKUP_ENC[num_z_bits][z]
                z = 0
                num_z_bits = 0

    if num_z_bits != 0:
        while num_z_bits not in _LOOKUP_ENC:
            z = (z << 1) + 1
            num_z_bits += 1

        s += _LOOKUP_ENC[num_z_bits][z]

    return s


def decode(s: str) -> bytes:
    """
    Decodes a Base32768 string into a bytes object.
    :param s: a Base32768 string
    :return:  the decoded bytes object
    """
    if type(s) is not str:
        raise TypeError('Argument must be str')

    length: int = len(s)

    # This length is a guess. There's a chance we allocate one more byte here
    # than we actually need. But we can count and slice it off later
    byte_arr: bytearray = bytearray(length * BITS_PER_CHAR // BITS_PER_BYTE)
    num_bytes: int = 0
    byte: int = 0
    num_byte_bits: int = 0

    for i, c in enumerate(s):

        if c not in _LOOKUP_DEC:
            raise ValueError(f'Unrecognised Base32768 character: {c}')

        num_z_bits, z = _LOOKUP_DEC[c]

        if num_z_bits != BITS_PER_CHAR and i != length - 1:
            raise ValueError(f'Secondary character found before end of input at position {i}')

        # Take most significant bit first
        for j in range(num_z_bits - 1, -1, -1):
            bit: int = (z >> j) & 1

            byte = (byte << 1) + bit
            num_byte_bits += 1

            if num_byte_bits == BITS_PER_BYTE:
                byte_arr[num_bytes] = byte
                num_bytes += 1
                byte = 0
                num_byte_bits = 0

    # Final padding bits! Requires special consideration!
    # Remember how we always pad with 1s?
    # Note: there could be 0 such bits, check still works though
    if byte != ((1 << num_byte_bits) - 1):
        raise ValueError('Padding mismatch')

    return bytes(byte_arr[:num_bytes])
