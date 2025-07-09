# Contributing to `datalad-api`

- [Developer cheat sheet](#developer-cheat-sheet)
- [Style guide](#contribution-style-guide)
- [CI workflows](#ci-workflows)


## Developer cheat sheet

[Hatch](https://hatch.pypa.io) is used as a convenience solution for packaging and development tasks.
Hatch takes care of managing dependencies and environments, including the Python interpreter itself.
If not installed yet, installing via [uv](https://docs.astral.sh/uv) is recommended
(`uv tool install hatch`).

Below is a list of some provided convenience commands.
An accurate overview of provided convenience scripts can be obtained by running: `hatch env show`.
All command setup can be found in `pyproject.toml`, and given alternatively managed dependencies, all commands can also be used without `hatch`.

### Run the tests (with coverage reporting)

```
hatch test [--cover] [--all]
```

This can also be used to run tests for a specific Python version only:

```
hatch test -i py=3.10 [<select tests>]
```

### Build the HTML documentation (under `docs/_build/html`)

```
hatch run docs:build
# clean with
hatch run docs:clean
```

### Check type annotations

```
hatch run types:check [<paths>]
```

### Check commit messages for compliance with [Conventional Commits](https://www.conventionalcommits.org)

```
hatch run cz:check-commits
```

### Show would-be auto-generated changelog for the next release

Run this command to see whether a commit series yields a sensible changelog
contribution.

```
hatch run cz:show-changelog
```

### Create a new release

```
hatch run cz:bump-version
```

The new version is determined automatically from the nature of the (conventional) commits made since the last release.
A changelog is generated and committed.

In cases where the generated changelog needs to be edited afterwards (typos, unnecessary complexity, etc.), the created version tag needs to be advanced.


### Build a new source package and wheel

```
hatch build
```

### Publish a new release to PyPi

```
hatch publish
```

## Contribution style guide

A contribution must be complete with code, tests, and documentation.

A high test-coverage is desirable.
Contributors should clarify why a contribution is not covered 100%.
Tests must be dedicated for the code of a particular contribution.
It is not sufficient, if other code happens to also exercise a new feature.

New code should be type-annotated.
At minimum, a type annotation of the main API (e.g., function signatures) is needed.
A dedicated CI run is testing type annotations.

Docstrings should be complete with information on parameters, return values, and exception behavior.
Documentation should be added to and rendered with the sphinx-based documentation.

### Conventional commits

Commits and commit messages must be [Conventional Commits](https://www.conventionalcommits.org).
Their compliance is checked for each pull request.
The following commit types are recognized:

- `feat`: introduces a new feature
- `fix`: address a problem, fix a bug
- `doc`: update the documentation
- `rf`: refactor code with no change of functionality
- `perf`: enhance performance of existing functionality
- `test`: add/update/modify test implementations
- `ci`: change CI setup
- `style`: beautification
- `chore`: results of routine tasks, such as changelog updates
- `revert`: revert a previous change
- `bump`: version update

Any breaking change must have at least one line of the format

    BREAKING CHANGE: <summary of the breakage>

in the body of the commit message that introduces the breakage.
Breaking changes can be introduced in any type of commit.
Any number of breaking changes can be described in a commit message (one per line).
Breaking changes trigger a major version update, and form a dedicated section in the changelog.

### Pull-requests

The projects uses pull requests (PR) for contributions.
However, PRs are considered disposable, and no essential information must be uniquely available in PR descriptions and discussions.
All important (meta-)information must be in commit messages.
It is perfectly fine to post a PR with *no* additional description.

### Imports

### Test output

Tests should be silent on stdout/stderr as much as possible.
In particular (but not only), result renderings of DataLad commands must no be produced, unless necessary for testing a particular feature.


## CI workflows

The addition of automation via CI workflows is welcome.
However, such workflows should not force developers to depend on, or have to wait for any particular service to run a workflow before they can discover essential outcomes.
When such workflows are added to online services, an equivalent setup for local execution should be added to the repository.
The `hatch` environments and tailored commands offer a straightforward, and discoverable method to fulfill this requirement (`hatch env show`).
