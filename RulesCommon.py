import re

# Variable names and values used by rule execution,
# will be automatically filled by Items
allowed_globals = {}


_escape = re.compile(r'[\'()[\]-]')

def escape_name(name):
    return _escape.sub('', name.replace(' ', '_'))

