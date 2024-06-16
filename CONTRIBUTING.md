# Contributing to strava-offline

## Development

Obtain the source code:

    $ git clone https://github.com/liskin/strava-offline

Setup Python virtual env and install missing dependencies:

    $ make

Make changes using your preferred editor.

Then invoke lints, tests, …:

    $ make check

These checks are also invoked in [CI (GitHub Actions)][ci] (against multiple
Python versions and also using different Linux distributions Python packages)
whenever a branch is pushed or a pull request is opened. You may need to
enable Actions in your fork's settings.

Other common tasks are available in the [Makefile](Makefile):

<!-- include tests/readme/make-help.md -->
<!--
    $ cd "$TESTDIR"/../..

    $ function make {
    >   command make --no-print-directory COLUMNS=120 "$@" 2>/dev/null
    > }
-->

    $ make help
    venv-system-site-packages: Setup ./.venv/ (--system-site-packages)
    venv: Setup ./.venv/
    pipx: Install locally using pipx
    pipx-site-packages: Install locally using pipx (--system-site-packages)
    check: Invoke all checks (lints, tests, readme)
    lint: Invoke lints
    lint-flake8:
    lint-mypy:
    lint-isort:
    test: Invoke tests
    test-pytest:
    test-prysk:
    readme: Update usage/examples in *.md and fail if it differs from version control
    dist: Build distribution artifacts (tar, wheel)
    twine-upload: Release to PyPI
    ipython: Invoke IPython in venv (not installed by default)
    clean: Clean all gitignored files/directories
    template-update: Re-render cookiecutter template into the template branch
    template-merge: Re-render cookiecutter template and merge into the current branch
    check-wheel: Check that the wheel we build works in a completely empty venv (i.e. check for unspecified dependencies)
    help: Display this help
<!-- end include tests/readme/make-help.md -->

[ci]: https://github.com/liskin/strava-offline/actions

## Style Guidelines

* Try to follow the existing style (where it's not already enforced by a
  linter). This applies to both code and git commits.

* Familiarise yourself with [the seven rules of a great Git commit
  message](https://cbea.ms/git-commit/#seven-rules).
