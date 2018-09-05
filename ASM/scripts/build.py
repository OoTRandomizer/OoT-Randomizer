#!/usr/bin/env python3
import argparse
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--pj64sym', help="Output path for PJ64 debugging symbols")
args = parser.parse_args()
pj64_sym_path = args.pj64sym
if pj64_sym_path:
    pj64_sym_path = os.path.realpath(pj64_sym_path)

script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

try:
    subprocess.call(['./armips', '-sym2', '../temp/symbols', '../src/build.asm'])
except FileNotFoundError:
    subprocess.call(['armips', '-sym2', '../temp/symbols', '../src/build.asm'])

if pj64_sym_path:
    subprocess.call(['python3', 'sym2pj64.py', '../temp/symbols', pj64_sym_path])
