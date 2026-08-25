This document describes how to manage dependency versions in a project.

# Python

* Python is a hard requirement for this project.
* We strive to always support the latest stable version of Python.
* We update the minimum Python version on January 1st of each year starting from January 2027.
  * As a one-time exception before the implementation of this policy, in August 2026 the minimum supported version was set to 3.13 as 3.12 only had a couple more months of support.
* The version is decided per https://scientific-python.org/specs/spec-0000/
  * The earliest version of python supported at the time of the change is the minimum.

* References that need to be updated when bumping the minimum version:
* README.md: Paragraph under link to website.
* Gui.py: lines 3 and 4
* OoTRandomizer.py: lines 3 and 4
* GUI/electron/src/preload.ts: in the `post.on('updateDynamicSetting', function (event)` handler.

# Node and npm

* Node and npm are soft-requirements necessary for running the GUI from the Gui.py script directly.
* ???

# numpy

* Pip installs this automatically when running the randomizer via the Gui.py or OoTRandomizer.py scripts.
* Version is pinned in `requirements.txt`
* We update the minimum numpy version on January 1st of each year starting from January 2027.
  * As a one-time exception before the implementation of this policy, in August 2026 the pinned version was set to 2.5.2 as that was the latest version of numpy supported at the time.
* The version is decided per https://scientific-python.org/specs/spec-0000/
  * The latest version of numpy supported at the time of the change is the version that gets pinned.

* There are no references to numpy versioning in the codebase itself.
