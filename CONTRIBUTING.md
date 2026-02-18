Here are various notes regarding the organization of this project:

# Getting started

If you're interested in contributing to randomizer development but you're not sure where to start, this section is for you.

* The best place to talk to the dev team and other contributors is #dev-public-talk on [our Discord server](https://discord.gg/ootrandomizer).
* Other good ways to contribute besides writing code are to test and review open pull requests. See the [Labels](#labels) section for details.
* You're not restricted to open GitHub issues. Feel free to PR any feature you think would be cool, or fix a bug you've run into that may not be extremely common.
* However, if you're looking for inspiration, we have a [Good First Issue](https://github.com/OoTRandomizer/OoT-Randomizer/issues?q=state%3Aopen%20label%3A%22Status%3A%20Good%20First%20Issue%22) label.
* The #dev-resources Discord channel has additional notes.
* If you're working on an issue and it's taking a while, leave a comment on the issue to avoid duplicate work, or consider opening a draft PR, especially if you're looking for help from other contributors.
* If you'd like to learn more about how this project is organized, keep reading.

# Labels

We use the following labels to organize our GitHub issues and pull requests. When a new issue/PR is opened, a dev team member will add all the relevant labels to it. If a label is skipped, that means it doesn't apply, e.g. if a new PR doesn't receive the “Status: Needs Testing” label, the person who labelled the PR considers it to be sufficiently tested.

## Type

* **Bug:** A bug report or bugfix PR.
* **Enhancement:** An issue requesting/tracking a new feature, or a PR adding one.
* **Maintenance:** Anything not covered by the other two labels, including code refactors, changes to infrastructure, dependency updates, changes to tests, etc.

An issue or especially PR may have multiple of these labels, e.g. if it implements a new feature but also fixes a bug as a side effect.

## Status

These labels are used to keep track of what still needs to be done for an issue to be resolved or a PR to be merged. A PR that no longer has any status labels will be merged by a maintainer soon.

* **Blocked:** There is another issue/PR that will need to be addressed first before this one can be resolved/merged. It will typically be linked from this issue/PR's comments.
* **Duplicate:** Given to issues/PRs that are closed because another issue/PR already exists for the same purpose.
* **Good First Issue:** We think that addressing this issue could be a good way for new contributors to get into development of the randomizer. If you would like to try but need help, feel free to ask in the issue comments or in #dev-public-talk on Discord.
* **Help Wanted:** We don't know how to address this issue, so we would be grateful if anyone with relevant knowledge could give more information, or even PR a fix.
* **Needs Review:** This label is given to every new PR. Someone (does not have to be a dev team member) other than the PR author should look at the code changes, point out anything they think could be improved, and ask about anything they're not sure about. We use the review types as follows:
    * **Comment:** Use this if you've only reviewed parts of the code.
    * **Request changes:** There are parts of the code that you think should be changed, and/or you have questions that need to be clarified.
    * **Approve:** You think this PR is ready to go. This label will be removed once a PR has at least one approving review and none requesting changes (or the reviewers who requested changes have gone inactive).
* **Needs Testing:** This label is given to every new PR. Someone (does not have to be a dev team member) should make sure the PR does what it says it does, usually by rolling a seed on the PR branch and either testing relevant parts of the game or checking the generated spoiler log, depending on the nature of the PR. Testing can be done by the PR author, so if you let us know what testing you've done on your PR and/or include screenshots or videos, we may skip adding this label entirely. The extent of testing required depends on how big the PR is; if you're not sure what exactly needs to be tested, ask in the PR thread or on Discord.
* **Under Consideration:** This label is given to every enhancement (new feature) issue/PR. The dev team will decide whether this feature is something we want in the randomizer, usually in one of [our calls](https://wiki.ootrandomizer.com/index.php?title=Dev_team_calls). An issue being accepted doesn't necessarily mean that the dev team will actively work on it though.
* **Waiting for Author:** This label is given to PRs when changes were requested, e.g. in a code review. It's also given to bug reports when we need more info from the reporter.
* **Waiting for Maintainers:** We need to do something to progress this issue/PR, e.g. make a decision on which way a new feature should work.
* **Waiting for Release:** This PR is otherwise ready to be merged, but we are currently in feature freeze (and this is an enhancement PR) or full freeze, and so we're waiting until after the upcoming release to merge it. See the [Release cycle](#release-cycle) section for details.
* **Wont Fix:** Given to bug reports that we've decided not to fix. The reason should be in the issue comments.

## Other

* **Changes Item Table:** All PRs that add or remove items from the item table in `ASM/c/item_table.c` are given this label so we can coordinate these changes across multiple open PRs, allowing infrastructure such as auto-trackers or multiworld plugins to add support for them before they're merged.
* **Component: […]:** Shows which parts of the randomizer codebase are changed by the PR, or are expected to require changes to resolve the issue. These labels are not defined rigorously, they're just intended to help get an overview of issues/PRs.
* **Racing Impact:** An issue/PR that's expected to affect the balance of competitive racing is given this label for the benefit of racing community members following along with development. This is especially the case for any changes to hints that aren't configurable or change defaults. Note that many dev team members aren't racers, so things may be missed here. It is recommended to keep an eye on the #dev-repo-updates Discord channel or watch the repository if you want to make sure you don't miss anything potentially relevant.
* **Trivial:** This PR doesn't actually change the semantics of the code, only its formatting or comments or the contents of text strings, and as such it does not need testing.

# Python

We support all versions of Python that are marked as “stable” or “security-fixes” in [the Python docs](https://docs.python.org/)' sidebar, and contributions will have to work on all of them. Unit tests are automatically run on the oldest and newest of them.

Additionally, we continue to support Python versions marked as “EOL” until there is a reason to drop support, no matter how minor. If your pull request doesn't work on an “EOL” version (but does work on all “stable” and “security-fixes” versions), you can raise the minimum supported version by editing the references to it in the randomizer codebase, including:

* `.github/workflows/python.yml`
* `Gui.py`
* `OoTRandomizer.py`
* `README.md`

# Updating old PRs

If your PR has been open for a while and you would like to update it for latest Dev:

* You don't need to resolve merge conflicts in generated files (in the `ASM/build` and `data/generated` directories); this will be done by the maintainer merging your PR. However, it may be useful to resolve them if you would like to rerun GitHub Actions on your PR.
* There's no strict policy on merging vs rebasing, but if you don't have a preference for one over the other, use a merge if your PR has previously been reviewed, rebase if not.

# Release cycle

Regular releases of the randomizer roughly follow this schedule:

* 3 months after the previous release was published, the codebase enters _feature freeze_: No new “enhancement” (new feature) pull requests will be merged until after the next release. Sometimes, exceptions are made for features that are particularly relevant for racing. During feature freeze, bug, maintenance, and preset PRs will continue to be merged as per usual (with possible exceptions made for PRs making very large code changes).
* Feature freeze lasts at least one week. We may also classify some open bugs as release-blocking if they were introduced since the last release and/or are high severity, in which case the codebase remains in feature freeze until they are fixed.
* After feature freeze, the codebase goes into _full freeze_, during which no changes are made to the code in order to allow our beta testers to test a build that's as close to the final release as possible. If critical issues are found, we go back to feature freeze.
* Full freeze also lasts at least one week and may take longer if beta tester activity is low.
* If no critical issues are found during beta testing, the release is published and any PRs labelled “waiting for release” are merged to start off the next release cycle.

There may also be hotfix releases which bypass this procedure, e.g. in case of a severe bug that wasn't caught in beta testing or in case of changes to racing presets.
