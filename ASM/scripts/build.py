#!/usr/bin/env/python3

import argparse
import json
import os
import re
from subprocess import check_call as call
from rom_diff import create_diff

parser = argparse.ArgumentParser()
parser.add_argument('--pj64sym', help="Output path for PJ64 debugging symbols")
parser.add_argument('--compile-c', action='store_true', help="Recompile C modules")

args = parser.parse_args()
pj64_sym_path = args.pj64sym
compile_c = args.compile_c

script_dir = os.path.dirname(os.path.realpath(__file__))
run_dir = script_dir + '/..'
os.chdir(run_dir)

# Compile code

os.environ['PATH'] = script_dir + os.pathsep + os.environ['PATH']

if compile_c:
    os.chdir(run_dir + '/c')
    call(['make'])

os.chdir(run_dir + '/src')
call(['armips', '-sym2', '../build/asm_symbols.txt', 'build.asm'])
os.chdir(run_dir)

with open('build/asm_symbols.txt', 'rb') as f:
    asm_symbols_content = f.read()
asm_symbols_content = asm_symbols_content.replace(b'\r\n', b'\n')
asm_symbols_content = asm_symbols_content.replace(b'\x1A', b'')
with open('build/asm_symbols.txt', 'wb') as f:
    f.write(asm_symbols_content)

# Parse symbols

c_sym_types = {}

with open('build/c_symbols.txt', 'r') as f:
    for line in f:
        m = re.match('''
                ^
                [0-9a-fA-F]+
                .*
                \.
                ([^\s]+)
                \s+
                [0-9a-fA-F]+
                \s+
                ([^.$][^\s]+)
                \s+$
            ''', line, re.VERBOSE)
        if m:
            sym_type = m.group(1)
            name = m.group(2)
            c_sym_types[name] = 'code' if sym_type == 'text' else 'data'

symbols = {}

with open('build/asm_symbols.txt', 'r') as f:
    for line in f:
        parts = line.strip().split(' ')
        if len(parts) < 2:
            continue
        address, sym_name = parts
        if address[0] != '8':
            continue
        if sym_name[0] in ['.', '@']:
            continue
        sym_type = c_sym_types.get(sym_name) or ('data' if sym_name.isupper() else 'code')
        symbols[sym_name] = {
            'type': sym_type,
            'address': address,
        }

# Output symbols

os.chdir(run_dir)

data_symbols = {}
for (name, sym) in symbols.items():
    if sym['type'] == 'data':
        addr = int(sym['address'], 16)
        if 0x80400000 <= addr < 0x80420000: #accept86
            addr = addr - 0x80400000 + 0x03480000
        else:
            continue
        data_symbols[name] = '{0:08X}'.format(addr)
with open('../data/generated/symbols.json', 'w') as f:
    json.dump(data_symbols, f, indent=4, sort_keys=True)
    
#accept86    
# symbols_RAM.json needed for hooks in working_navi.py
#I put the hooks there, because I don´t want to change code flow of main rando
for (name, sym) in symbols.items():
    if sym['type'] == 'data':
        addr = int(sym['address'], 16)
        data_symbols[name] = '{0:08X}'.format(addr)
with open('../data/generated/symbols_RAM.json', 'w') as f:
    json.dump(data_symbols, f, indent=4, sort_keys=True)
    

if pj64_sym_path:
    pj64_sym_path = os.path.realpath(pj64_sym_path)
    with open(pj64_sym_path, 'w') as f:
        key = lambda pair: pair[1]['address']
        for sym_name, sym in sorted(symbols.items(), key=key):
            f.write('{0},{1},{2}\n'.format(sym['address'], sym['type'], sym_name))

# Diff ROMs
create_diff('roms/base.z64', 'roms/patched.z64', '../data/generated/rom_patch.txt')
