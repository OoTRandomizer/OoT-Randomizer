from Utils import VersionError
import sys, json, logging, os
import urllib.request
from urllib.error import URLError, HTTPError
from version import __version__

base_url = 'https://api.github.com/repos/TestRunnerSRL/Oot-randomizer'
logger = logging.getLogger('')

# Used to make all get requests and parse the json
def get_request(endpoint, base=base_url, is_json=True):
    url = base + endpoint
    try:
        #print("Getting " + url)
        with urllib.request.urlopen(url) as data:
            if is_json:
                return json.loads(data.read().decode("utf-8"))
            else:
                return data.read()
    except (URLError, HTTPError) as e:
        logger.error("Could not connect to " + url)
        logger.error(str(e))
        sys.exit(1)

def get_changes():
    current_version = __version__.replace(' f.LUM', '')

    all_versions = get_request('/tags?per_page=100') # we can pass per_page to get more pages, up to 100
    version_map = {version['name'] : version for version in all_versions}
    version_numbers = list(version_map.keys())
    version_numbers.sort(key=lambda s: list(map(int, s.replace('v', '0').split('.'))))
    latest_version = version_numbers[-1]

    if current_version not in version_numbers:
        print(version_numbers)
        raise VersionError("Version " + current_version + " is too old to auto update from. Please downlad the latest version at " + version_map[latest_version]['zipball_url'])

    elif current_version == str(latest_version):
        logger.error("You are already on the latest version " + latest_version)
        sys.exit(1)

    return get_request('/compare/%s...%s' % (version_map[current_version]['commit']['sha'], version_map[latest_version]['commit']['sha']))['files']
    
def apply_change(file_change):

    path = file_change['filename']
    change_type = file_change['status']
    data_url = file_change['raw_url']

    nice_text = {'modified' : 'updating', 'added' : 'adding', 'renamed' : 'renaming', 'removed' : 'removing' }
    print(nice_text[change_type] + " " + path, flush=True)

    # Get the raw data
    if change_type in ['modified', 'added', 'renamed']:
        raw_data = get_request(data_url, base='', is_json=False)

    file_from = None
    file_to = None

    # Back up files so we can roll back if needed
    if change_type in ['removed', 'modified']:
        file_from = path + '.bak'
        os.rename(path, file_from)
    elif change_type == 'renamed':
        file_from = file_change['previous_filename'] + '.bak'
        os.rename(file_change['previous_filename'], file_from)
    else:
        file_from = None

    # A modification, addition, or rename will just rewrite the entire file for simplicity
    if change_type == 'removed':
        file_to = None
    else:
        file_to = path
        with open(path, 'wb+') as file:
            file.write(raw_data)

    return (change_type, file_from, file_to)

compare = get_changes()

changes = []

try:
    for c in compare:
        changes.append(apply_change(c))
except Exception as e:
    print("ERROR: " + str(e))
    print("Trying to recover files")
    # try and restore files
    # TODO
    sys.exit(1)

# clean up bak ups
for change_type, file_from, file_to in changes:
    if change_type in ['removed', 'modified', 'renamed']:
        print("Removing " + file_from)
        os.remove(file_from)


