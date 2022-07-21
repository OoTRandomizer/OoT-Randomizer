# This script is called by GitHub Actions, see .github/workflows/python.yml

import json
import sys
from io import StringIO
import unittest

import Unittest as Tests
from SettingsList import logic_tricks
from Utils import data_path

num_errors = 0

def error(msg):
    global num_errors

    print(msg, file=sys.stderr)
    num_errors += 1


# Run Unit Tests
stream = StringIO()
runner = unittest.TextTestRunner(stream=stream)
tests = filter(lambda cls: isinstance(cls, type) and issubclass(cls, unittest.TestCase), Tests.__dict__.values())
suite = unittest.TestSuite()
for test in tests:
    suite.addTests(unittest.makeSuite(test))
result = runner.run(suite)
print(f'Tests run: {result.testsRun}.')
stream.seek(0)
print(f'Test output:\n{stream.read()}')
if result.errors:
    error('Unit Tests had an error, see output above.')

# Check for tricks missing from Hell Mode preset.
with open(data_path('presets_default.json'), encoding='utf-8') as f:
    presets = json.load(f)
    for trick in logic_tricks.values():
        if trick['name'] not in presets['Hell Mode']['allowed_tricks']:
            error(f'Logic trick {trick["name"]!r} missing from Hell Mode preset.')

if num_errors > 0:
    print(f'CI failed with {num_errors} errors.', file=sys.stderr)
    sys.exit(1)
else:
    print(f'CI checks successful.')
