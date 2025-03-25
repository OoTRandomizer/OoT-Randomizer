from ctypes import *
import os
import sys
from binascii import hexlify

# Import the shared library. Need to check for windows vs. linux vs. mac
shared_lib = "vadpcm_enc_shared"
if sys.platform == 'darwin':
    shared_lib = "vadpcm_enc_shared_mac"

try:
    lib = CDLL(os.path.join(os.path.dirname(os.path.realpath(__file__)),shared_lib))
except:
    raise Exception(os.path.curdir)
# Converts raw 16-bit samples to ADPCM compressed bytes
def adpcm_encode(frames: bytes, num_frames: int):
    # Convert params to ctypes
    c_in_buffer = c_char_p(frames)
    c_num_frames = c_int(num_frames)
    c_out = create_string_buffer(2 * num_frames) # Create a buffer that will definitely be big enough to hold the output

    # Call the library function
    vadpcm_enc_wrapper = lib.vadpcm_enc_wrapper
    outsize = vadpcm_enc_wrapper(c_in_buffer, c_num_frames, c_out)

    # ADPCM compressed samples are in c_out.raw
    # number of samples is returned by the function in outsize
    return c_out.raw[0:outsize]
