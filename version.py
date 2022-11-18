__version__ = '6.9.14'

# This is a supplementary version number for branches based off of main dev.
supplementary_version = 0

# Pick a unique identifier byte for your fork if you are intending to have a long-lasting branch.
# This will be 0x00 for main releases and 0x01 for main dev.
branch_identifier = 0x01

# URL to your branch on GitHub.
branch_url = 'https://github.com/TestRunnerSRL/OoT-Randomizer/tree/Dev'

# This is named __version__ at the top for compatability with older versions trying to version check.
base_version = __version__

# And finally, the completed version string. This is what is displayed and used for salting seeds.
__version__ = f'{base_version} f.LUM'
