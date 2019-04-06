#!/usr/bin/env/python3

import json
import struct
import sys

def main():
    if len(sys.argv) < 4:
        raise RuntimeError("Usage: python rom_diff.py BASE_FILE COMPARISON_FILE OUTPUT_FILE")

    base_path = sys.argv[1]
    compare_path = sys.argv[2]
    output_path = sys.argv[3]
    create_diff(base_path, compare_path, output_path)

chunk_size = 4096
uint32 = struct.Struct('>I')

def unequal_chunks(file1, file2):
    addr = 0
    while True:
        chunk1 = file1.read(chunk_size)
        chunk2 = file2.read(chunk_size)
        if not chunk1:
            return
        if chunk1 != chunk2:
            words1 = [x[0] for x in uint32.iter_unpack(chunk1)]
            words2 = [x[0] for x in uint32.iter_unpack(chunk2)]
            yield (addr, words1, words2)
        addr += chunk_size

def create_diff(base_path, compare_path, output_path):
    diffs = []
    with open(base_path, 'rb') as base_f, open(compare_path, 'rb') as comp_f:
        for (addr, base_words, comp_words) in unequal_chunks(base_f, comp_f):
            for j in range(len(comp_words)):
                if comp_words[j] != base_words[j]:
                    diffs.append((addr + 4*j, comp_words[j]))

    with open(output_path, 'w') as out_f:
        for (addr, word) in diffs:
            out_f.write('{0:x},{1:x}\n'.format(addr, word))

if __name__ == '__main__':
    main()
