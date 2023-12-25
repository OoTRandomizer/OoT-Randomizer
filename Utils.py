from __future__ import annotations
import io
import json
import logging
import os
import re
import subprocess
import sys
import urllib.request
from collections.abc import Sequence
from typing import AnyStr, Optional, Any
from urllib.error import URLError, HTTPError

from version import __version__, base_version, supplementary_version, branch_url


def is_bundled() -> bool:
    return getattr(sys, 'frozen', False)


def local_path(path: str = '') -> str:
    if not hasattr(local_path, "cached_path"):
        local_path.cached_path = None

    if local_path.cached_path is not None:
        return os.path.join(local_path.cached_path, path)

    if is_bundled():
        # we are running in a bundle
        local_path.cached_path = os.path.dirname(os.path.realpath(sys.executable))
    else:
        # we are running in a normal Python environment
        local_path.cached_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(local_path.cached_path, path)


def data_path(path: str = '') -> str:
    if not hasattr(data_path, "cached_path"):
        data_path.cached_path = None

    if data_path.cached_path is not None:
        return os.path.join(data_path.cached_path, path)

    # Even if it's bundled we use __file__
    # if it's not bundled, then we want to use the source.py dir + Data
    # if it's bundled, then we want to use the extraction dir + Data
    data_path.cached_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

    return os.path.join(data_path.cached_path, path)


def default_output_path(path: str) -> str:
    if path == '':
        path = local_path('Output')

    if not os.path.exists(path):
        os.mkdir(path)
    return path


def read_logic_file(file_path: str):
    json_string = ""
    with io.open(file_path, 'r') as file:
        for line in file.readlines():
            json_string += line.split('#')[0].replace('\n', ' ')
    json_string = re.sub(' +', ' ', json_string)
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as error:
        raise Exception("JSON parse error around text:\n" + \
                        json_string[error.pos-35:error.pos+35] + "\n" + \
                        "                                   ^^\n")


def open_file(filename: str) -> None:
    if sys.platform == 'win32':
        os.startfile(filename)
    else:
        open_command = 'open' if sys.platform == 'darwin' else 'xdg-open'
        subprocess.call([open_command, filename])


def get_version_bytes(a: str, b: int = 0x00, c: int = 0x00) -> list[int]:
    version_bytes = [0x00, 0x00, 0x00, b, c]

    if not a:
        return version_bytes

    sa = a.replace('v', '').replace(' ', '.').split('.')

    for i in range(0, 3):
        try:
            version_byte = int(sa[i])
        except ValueError:
            break
        version_bytes[i] = version_byte

    return version_bytes


def compare_version(a: str, b: str) -> int:
    if not a and not b:
        return 0
    elif a and not b:
        return 1
    elif not a and b:
        return -1

    sa = get_version_bytes(a)
    sb = get_version_bytes(b)

    for i in range(0, 3):
        if sa[i] > sb[i]:
            return 1
        if sa[i] < sb[i]:
            return -1
    return 0


class VersionError(Exception):
    pass


def check_version(checked_version: str) -> None:
    if not hasattr(check_version, "base_regex"):
        check_version.base_regex = re.compile("""^[ \t]*__version__ = ['"](.+)['"]""", re.MULTILINE)
        check_version.supplementary_regex = re.compile(r"^[ \t]*supplementary_version = (\d+)$", re.MULTILINE)
        check_version.full_regex = re.compile("""^[ \t]*__version__ = f['"]*(.+)['"]""", re.MULTILINE)
        check_version.url_regex = re.compile("""^[ \t]*branch_url = ['"](.+)['"]""", re.MULTILINE)

    if compare_version(checked_version, __version__) < 0:
        try:
            with urllib.request.urlopen(f'{branch_url.replace("https://github.com", "https://raw.githubusercontent.com").replace("tree/", "")}/version.py') as versionurl:
                version_file = versionurl.read().decode("utf-8")

                base_match = check_version.base_regex.search(version_file, re.MULTILINE)
                supplementary_match = check_version.supplementary_regex.search(version_file, re.MULTILINE)
                full_match = check_version.full_regex.search(version_file, re.MULTILINE)
                url_match = check_version.url_regex.search(version_file, re.MULTILINE)

                remote_base_version = base_match.group(1) if base_match else ""
                remote_supplementary_version = int(supplementary_match.group(1)) if supplementary_match else 0
                remote_full_version = full_match.group(1) if full_match else remote_base_version
                remote_full_version = remote_full_version \
                    .replace('{base_version}', remote_base_version) \
                    .replace('{supplementary_version}', str(remote_supplementary_version))
                remote_branch_url = url_match.group(1) if url_match else ""

                upgrade_available = False
                if compare_version(remote_base_version, base_version) > 0:
                    upgrade_available = True
                elif compare_version(remote_base_version, base_version) == 0 and remote_supplementary_version > supplementary_version:
                    upgrade_available = True

                if upgrade_available:
                    raise VersionError("You are on version " + __version__ + ", and the latest is version " + remote_full_version + ".")
        except (URLError, HTTPError) as e:
            logger = logging.getLogger('')
            logger.warning("Could not fetch latest version: " + str(e))


# From the pyinstaller Wiki: https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess
# Create a set of arguments which make a ``subprocess.Popen`` (and
# variants) call work with or without Pyinstaller, ``--noconsole`` or
# not, on Windows and Linux. Typical use::
#   subprocess.call(['program_to_run', 'arg_1'], **subprocess_args())
def subprocess_args(include_stdout: bool = True) -> dict[str, Any]:
    # The following is true only on Windows.
    if hasattr(subprocess, 'STARTUPINFO'):
        # On Windows, subprocess calls will pop up a command window by default
        # when run from Pyinstaller with the ``--noconsole`` option. Avoid this
        # distraction.
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so
        # it will.
        env = os.environ
    else:
        si = None
        env = None

    # ``subprocess.check_output`` doesn't allow specifying ``stdout``::
    # So, add it only if it's needed.
    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}

    # On Windows, running this from the binary produced by Pyinstaller
    # with the ``--noconsole`` option requires redirecting everything
    # (stdin, stdout, stderr) to avoid an OSError exception
    # "[Error 6] the handle is invalid."
    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env})
    return ret


def run_process(logger: logging.Logger, args: Sequence[str], stdin: Optional[AnyStr] = None) -> None:
    process = subprocess.Popen(args, bufsize=1, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    filecount = None
    if stdin is not None:
        process.communicate(input=stdin)
    else:
        while True:
            line = process.stdout.readline()
            if line != b'':
                find_index = line.find(b'files remaining')
                if find_index > -1:
                    files = int(line[:find_index].strip())
                    if filecount is None:
                        filecount = files
                logger.info(line.decode('utf-8').strip('\n'))
            else:
                break


# https://stackoverflow.com/a/23146126
def try_find_last(source_list: Sequence[Any], sought_element: Any) -> Optional[int]:
    for reverse_index, element in enumerate(reversed(source_list)):
        if element == sought_element:
            return len(source_list) - 1 - reverse_index
    return None


def find_last(source_list: Sequence[Any], sought_element: Any) -> int:
    last = try_find_last(source_list, sought_element)
    if last is None:
        raise Exception(f"Element {sought_element} not found in sequence {source_list}.")
    return last
