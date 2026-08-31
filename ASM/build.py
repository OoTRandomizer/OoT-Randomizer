#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

import argparse
import json
import platform
import re
import shlex
import shutil
from subprocess import check_call as call, check_output, CalledProcessError, DEVNULL
from rom_diff import create_diff
from ntype import BigStream
from crc import calculate_crc

parser = argparse.ArgumentParser()
parser.add_argument('--pj64sym', help="Output path for Project64 debugging symbols")
parser.add_argument('--compile-c', action='store_true', help="Recompile C modules. This is the default")
parser.add_argument('--no-compile-c', action='store_true', help="Do not recompile C modules")
parser.add_argument('--dump-obj', action='store_true', help="Dumps extra object info for debugging purposes. Does nothing with --no-compile-c")
parser.add_argument('--diff-only', action='store_true', help="Creates diff output without running armips")
parser.add_argument('--mips-binutils-prefix', type=str, default="mips64-", help="Use a different prefix for N64 toolchain")
parser.add_argument('--debug-c', action='store_true', help="Define DEBUG_MODE 1 for C modules")
parser.add_argument('--check-toolchains', action='store_true', help="Show the expected and selected path for every required ASM file and tool, then exit")

args = parser.parse_args()
pj64_sym_path = args.pj64sym
compile_c = not args.no_compile_c
dump_obj = args.dump_obj
diff_only = args.diff_only
mips_binutils_prefix = args.mips_binutils_prefix
debug_c = args.debug_c
check_toolchains = args.check_toolchains

root_dir = os.path.dirname(os.path.realpath(__file__))
tools_dir = os.path.join(root_dir, 'tools')
# Supported project-local layouts:
#   ASM/tools/<tool>
#   ASM/tools/bin/<tool>
#   ASM/tools/n64/bin/<tool>
tools_bin_dir = os.path.join(tools_dir, 'bin')
n64_bin_dir = os.path.join(tools_dir, 'n64', 'bin')
# Generated POSIX compiler launchers use one platform-neutral location.
toolchain_dir = os.path.join(tools_dir, 'toolchain')
toolchain_bin_dir = os.path.join(toolchain_dir, 'bin')
toolchain_driver_dir = os.path.join(toolchain_dir, 'gcc-driver')


def is_executable(path):
    return bool(path and os.path.isfile(path) and os.access(path, os.X_OK))


def prepend_path(*directories):
    current = os.environ.get('PATH', '').split(os.pathsep)
    ordered = []
    for directory in directories:
        if directory and directory not in ordered:
            ordered.append(directory)
    for directory in current:
        if directory and directory not in ordered:
            ordered.append(directory)
    os.environ['PATH'] = os.pathsep.join(ordered)


def find_toolchain_prefix(tool_prefix):
    """Find a complete N64 prefix without changing the normal tool search order."""
    gcc_name = tool_prefix + 'gcc'
    candidates = [
        os.environ.get('OOTR_N64_PREFIX'),
        os.path.join(tools_dir, 'n64'),
    ]

    # A local executable or symlink can reveal the complete installation prefix.
    for gcc_path in (
        os.path.join(tools_dir, gcc_name),
        os.path.join(tools_bin_dir, gcc_name),
        os.path.join(n64_bin_dir, gcc_name),
        shutil.which(gcc_name),
    ):
        if gcc_path and os.path.exists(gcc_path):
            real_gcc = os.path.realpath(gcc_path)
            candidates.append(os.path.dirname(os.path.dirname(real_gcc)))

    # Homebrew exposes every tap formula named n64 through the same opt prefix.
    # Adding these normal installation paths avoids embedding brew-specific
    # command handling in the build script and also handles PATH shadowing.
    if platform.system() == 'Darwin':
        candidates.extend(('/opt/homebrew/opt/n64', '/usr/local/opt/n64'))

    required = ('gcc', 'as', 'ld', 'objdump', 'objcopy')
    checked = set()
    for candidate in candidates:
        if not candidate:
            continue
        candidate = os.path.realpath(os.path.expanduser(candidate))
        if candidate in checked:
            continue
        checked.add(candidate)
        bindir = os.path.join(candidate, 'bin')
        if all(is_executable(os.path.join(bindir, tool_prefix + tool)) for tool in required):
            return candidate
    return None


def write_executable(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='\n') as stream:
        stream.write(content)
    os.chmod(path, 0o755)


def prepare_toolchain(tool_prefix):
    """Prepare one consistent toolchain path on every supported platform."""
    prepend_path(tools_dir, tools_bin_dir, n64_bin_dir)

    prefix = find_toolchain_prefix(tool_prefix)
    if not prefix:
        return None

    real_bin = os.path.join(prefix, 'bin')
    prepend_path(real_bin, tools_dir, tools_bin_dir, n64_bin_dir)

    # Windows toolchains are executable files and continue to run directly.
    # POSIX hosts use the same tools/toolchain layout so GCC and its assembler
    # always come from one prefix. Apple Silicon adds only the environment
    # isolation that was required by the native Homebrew toolchain.
    if os.name != 'nt':
        real_gcc = os.path.join(real_bin, tool_prefix + 'gcc')
        real_gxx = os.path.join(real_bin, tool_prefix + 'g++')
        real_as = os.path.join(real_bin, tool_prefix + 'as')
        driver_as = os.path.join(toolchain_driver_dir, 'as')
        isolate_assembler = platform.system() == 'Darwin' and platform.machine() == 'arm64'

        if isolate_assembler:
            assembler_script = '\n'.join([
                '#!/bin/sh',
                'set -eu',
                'exec /usr/bin/env -i \\',
                '  PATH="/usr/bin:/bin" \\',
                '  HOME="${HOME:-/tmp}" \\',
                '  TMPDIR="${TMPDIR:-/tmp}" \\',
                '  LANG=C \\',
                '  LC_ALL=C \\',
                '  ' + shlex.quote(real_as) + ' "$@"',
                '',
            ])
        else:
            assembler_script = '\n'.join([
                '#!/bin/sh',
                'set -eu',
                'exec ' + shlex.quote(real_as) + ' "$@"',
                '',
            ])
        write_executable(driver_as, assembler_script)

        for name, compiler in (
            (tool_prefix + 'gcc', real_gcc),
            (tool_prefix + 'g++', real_gxx),
        ):
            if not is_executable(compiler):
                continue
            compiler_script = '\n'.join([
                '#!/bin/sh',
                'set -eu',
                'exec ' + shlex.quote(compiler) + ' -B' + shlex.quote(toolchain_driver_dir + os.sep) + ' "$@"',
                '',
            ])
            write_executable(os.path.join(toolchain_bin_dir, name), compiler_script)

        # Expose the remaining tools from the same prefix in the same generated
        # directory. This keeps Linux and macOS layouts identical and prevents
        # another installation earlier in PATH from supplying ld or objcopy.
        os.makedirs(toolchain_bin_dir, exist_ok=True)
        wrapper_names = {tool_prefix + 'gcc', tool_prefix + 'g++'}
        for name in os.listdir(real_bin):
            if not name.startswith(tool_prefix) or name in wrapper_names:
                continue
            source = os.path.join(real_bin, name)
            target = os.path.join(toolchain_bin_dir, name)
            if not is_executable(source):
                continue
            if os.path.lexists(target):
                os.unlink(target)
            os.symlink(os.path.realpath(source), target)

        prepend_path(toolchain_bin_dir, real_bin, tools_dir, tools_bin_dir, n64_bin_dir)
        if isolate_assembler:
            os.environ.pop('COMPILER_PATH', None)
            os.environ.pop('GCC_EXEC_PREFIX', None)
            print(f'build.py: isolated assembler: {driver_as}')

    print(f'build.py: toolchain prefix: {prefix}')
    return prefix


def command_version(path, *args):
    try:
        output = check_output([path, *args], text=True, stderr=DEVNULL).strip()
        return output.splitlines()[0] if output else 'version unavailable'
    except (CalledProcessError, OSError):
        return 'version unavailable'


def display_path_check(label, expected_path, exists, actual_path=None, detail=None):
    status = 'OK' if exists else 'MISSING'
    print(f'  [{status}] {label}')
    print(f'       expected: {expected_path}')
    print(f'       actual:   {actual_path if actual_path else "not found"}')
    if detail:
        print(f'       detail:   {detail}')


def local_command_candidates(name, is_mips=False):
    candidates = [
        os.path.join(tools_dir, name),
        os.path.join(tools_bin_dir, name),
        os.path.join(n64_bin_dir, name),
    ]
    if is_mips:
        candidates.append(os.path.join(toolchain_bin_dir, name))
        prefix = os.environ.get('OOTR_N64_PREFIX')
        if prefix:
            candidates.append(os.path.join(prefix, 'bin', name))
    return candidates


def display_command_check(name, version_args, include_project_paths=True, is_mips=False):
    selected = shutil.which(name)
    valid = is_executable(selected)
    print(f'  [{"OK" if valid else "MISSING"}] {name}')

    if include_project_paths:
        candidates = local_command_candidates(name, is_mips)
        print('       expected:')
        for candidate in candidates:
            state = 'present' if is_executable(candidate) else 'absent'
            print(f'         - [{state}] {candidate}')
        print('         - [environment] PATH')
    else:
        print('       expected: executable available in PATH')

    print(f'       selected: {selected if selected else "not found"}')
    if valid:
        real_path = os.path.realpath(selected)
        if real_path != selected:
            print(f'       resolved: {real_path}')
        print(f'       version:  {command_version(selected, *version_args)}')
    return valid, selected


def check_toolchain_requirements(tool_prefix):
    print('OoTR ASM toolchain check')
    print(f'  host: {platform.system()} {platform.machine()}')
    print(f'  ASM directory: {root_dir}')
    print(f'  MIPS prefix: {tool_prefix}')
    prefix_override = os.environ.get('OOTR_N64_PREFIX')
    print(f'  OOTR_N64_PREFIX: {prefix_override if prefix_override else "not set"}')
    ok = True

    required_files = [
        'Makefile',
        'linker_script.ld',
        'ootSymbols.ld',
        os.path.join('src', 'build.asm'),
        os.path.join('src', 'addresses.asm'),
        os.path.join('src', 'boot.asm'),
        os.path.join('c', 'util.c'),
    ]
    print('Project files:')
    for relative in required_files:
        expected = os.path.abspath(os.path.join(root_dir, relative))
        exists = os.path.isfile(expected)
        display_path_check(relative, expected, exists, expected if exists else None)
        ok = ok and exists

    print('Base ROM:')
    rom_path = os.path.abspath(os.path.join(root_dir, 'roms', 'base.z64'))
    if os.path.isfile(rom_path):
        size = os.path.getsize(rom_path)
        valid = size == 0x4000000
        status = 'OK' if valid else 'INVALID'
        print(f'  [{status}] roms/base.z64')
        print(f'       expected: {rom_path}')
        print(f'       actual:   {rom_path}')
        print(f'       size:     {size:#x} bytes; expected 0x4000000 bytes (64 MiB)')
        ok = ok and valid
    else:
        display_path_check('roms/base.z64', rom_path, False)
        ok = False

    print('Executables:')
    command_specs = [
        ('armips', ['--version'], True, False),
        ('make', ['--version'], False, False),
        (tool_prefix + 'gcc', ['--version'], True, True),
        (tool_prefix + 'as', ['--version'], True, True),
        (tool_prefix + 'ld', ['--version'], True, True),
        (tool_prefix + 'objdump', ['--version'], True, True),
        (tool_prefix + 'objcopy', ['--version'], True, True),
    ]
    resolved = {}
    for name, version_args, include_project_paths, is_mips in command_specs:
        valid, selected = display_command_check(name, version_args, include_project_paths, is_mips)
        resolved[name] = selected
        ok = ok and valid

    print('GCC assembler selection:')
    gcc_name = tool_prefix + 'gcc'
    gcc_path = resolved.get(gcc_name)
    if gcc_path:
        try:
            reported = check_output([gcc_path, '-print-prog-name=as'], text=True, stderr=DEVNULL).strip()
            assembler = reported
            if assembler and not os.path.isabs(assembler):
                assembler = shutil.which(assembler) or assembler
            valid = is_executable(assembler)
            print(f'  [{"OK" if valid else "INVALID"}] assembler selected by {gcc_name}')
            print(f'       query:    {gcc_path} -print-prog-name=as')
            print(f'       reported: {reported if reported else "not reported"}')
            print(f'       actual:   {assembler if assembler else "not found"}')
            if valid:
                real_assembler = os.path.realpath(assembler)
                if real_assembler != assembler:
                    print(f'       resolved: {real_assembler}')
            ok = ok and valid
        except (CalledProcessError, OSError):
            print(f'  [INVALID] assembler selected by {gcc_name}')
            print(f'       query:    {gcc_path} -print-prog-name=as')
            print('       actual:   query failed')
            ok = False
    else:
        print(f'  [MISSING] assembler selected by {gcc_name}')
        print(f'       query:    unavailable because {gcc_name} was not found')
        print('       actual:   not found')
        ok = False

    print(f'Result: {"OK" if ok else "FAILED"}')
    return ok


if compile_c or check_toolchains:
    prepare_toolchain(mips_binutils_prefix)
else:
    prepend_path(tools_dir, tools_bin_dir, n64_bin_dir)

if check_toolchains:
    sys.exit(0 if check_toolchain_requirements(mips_binutils_prefix) else 1)


run_dir = root_dir

# Compile code

os.chdir(run_dir)

base_rom_size = os.stat('roms/base.z64').st_size
if base_rom_size != 0x400_0000:
    sys.exit(f'build.py: roms/base.z64 should be 0x4000000 bytes (64 MiB), but yours is 0x{base_rom_size:x} bytes ({base_rom_size / (1024 ** 2)} MiB). Make sure you have an uncompressed base ROM (see ../bin/Decompress).')

if compile_c:
    clist = ['make']
    if os.path.isdir(os.path.join(run_dir, 'build', 'bin')):
        call([*clist, 'clean'])
    clist.append(f'MIPS_BINUTILS_PREFIX={mips_binutils_prefix}')
    if debug_c:
        clist.append(f'DEBUG_MODE=1')
    if dump_obj:
        clist.append('RUN_OBJDUMP=1')
    try:
        call(clist)
    except CalledProcessError as e:
        print(e.output)
        exit(e.returncode)

if not diff_only:
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
        m = re.match(r'''
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

# Loop through a second time, add lengths to each data symbol
# This could probably be optimized to run in a single pass :)
with open('build/asm_symbols.txt', 'r') as f:
    for line in f:
        parts = line.strip().split(' ')
        if len(parts) < 2:
            continue
        address, sym_name = parts
        if sym_name.startswith('.'):
            # split on the ':' to get the length, in hex
            type, hex_length = sym_name.split(':')
            for symbol, sym_data in symbols.items():
                if sym_data['address'] == address and sym_data['type'] == 'data':
                    sym_data['length'] = int(hex_length, 16)

# Output symbols

os.chdir(run_dir)

PAYLOAD_START = int(symbols['PAYLOAD_START']['address'], 16)
PAYLOAD_END = int(symbols['PAYLOAD_END']['address'], 16)
data_symbols = {}
patch_symbols = {}
for (name, sym) in symbols.items():
    if sym['type'] == 'data':
        addr = int(sym['address'], 16)
        if PAYLOAD_START <= addr < PAYLOAD_END:
            addr = addr - 0x80400000 + 0x03480000
            data_symbols[name] = {
                'address': f'{addr:08X}',
                'length': sym.get('length', 0),
            }
        else:
            patch_symbols[name] = addr

with open('../data/generated/symbols.json', 'w+', newline='\n') as f:
    json.dump(data_symbols, f, indent=4, sort_keys=True)

with open('../data/generated/patch_symbols.json', 'w+', newline='\n') as f:
    json.dump(patch_symbols, f, indent=4, sort_keys=True)

if pj64_sym_path:
    pj64_sym_path = os.path.realpath(pj64_sym_path)
    with open(pj64_sym_path, 'w+') as f:
        key = lambda pair: pair[1]['address']
        for sym_name, sym in sorted(symbols.items(), key=key):
            f.write('{0},{1},{2}\n'.format(sym['address'], sym['type'], sym_name))


with open('roms/patched.z64', 'r+b') as stream:
    buffer = bytearray(stream.read(0x101000))
    crc = calculate_crc(BigStream(buffer))
    stream.seek(0x10)
    stream.write(bytearray(crc))

# Diff ROMs
create_diff('roms/base.z64', 'roms/patched.z64', '../data/generated/rom_patch.txt')
