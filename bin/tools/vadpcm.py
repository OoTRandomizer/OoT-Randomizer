from ctypes import *

so_file = "bin/tools/test.so"
my_functions = CDLL(so_file)

print(my_functions)