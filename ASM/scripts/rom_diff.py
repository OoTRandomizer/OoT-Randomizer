#!/usr/bin/env python3

import json
import sys

if len(sys.argv) < 4:
    raise RuntimeError("Usage: python3 rom_diff.py BASE_FILE COMPARISON_FILE OUTPUT_FILE")

base_path = sys.argv[1]
compare_path = sys.argv[2]
output_path = sys.argv[3]

with open(base_path, 'rb') as base_file:
    base_data = base_file.read()
with open(compare_path, 'rb') as compare_file:
    compare_data = compare_file.read()

diffs = []
run = []
for i in range(0, len(base_data)):
    if base_data[i] != compare_data[i]:
        if run and run[-1][0] != i - 1:
            diffs.append({ run[0][0]: [value for (_, value) in run] })
            run = []
        run.append((i, compare_data[i]))
if run:
    diffs.append({ run[0][0]: [value for (_, value) in run] })

with open(output_path, 'w') as output_file:
    json.dump(diffs, output_file)
