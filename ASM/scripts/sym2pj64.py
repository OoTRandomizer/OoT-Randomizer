#!/usr/bin/env python3

import sys

if len(sys.argv) < 3:
    raise RuntimeError("Usage: python3 sym2pj64.py IN_FILE OUT_FILE")

in_path = sys.argv[1]
out_path = sys.argv[2]

in_file = open(in_path, 'r')
out_file = open(out_path, 'w')

for line in in_file:
    parts = line.strip().split(' ')
    if len(parts) < 2:
        continue
    address, label = parts
    if address[0] != '8':
        continue
    if label[0] == '.':
        continue
    label_type = 'data' if label.isupper() else 'code'
    out_line = ','.join([address, label_type, label])
    print(out_line, file=out_file)

in_file.close()
out_file.close()
