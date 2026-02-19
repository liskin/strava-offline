# Contributing to strava-offline

## Development

Obtain the source code:

    $ git clone https://github.com/liskin/strava-offline

Setup Python virtual env and install missing dependencies:

    $ just

Make changes using your preferred editor.

Then invoke lints, tests, …:

    $ just check

These checks are also invoked in [CI (GitHub Actions)][ci] (against multiple
Python versions and also using different Linux distributions Python packages)
whenever a branch is pushed or a pull request is opened. You may need to
enable Actions in your fork's settings.

Other common tasks are available in the [Justfile](Justfile):

<!-- include tests/readme/make-help.md -->
<!--
    $ cd "$TESTDIR"/../..

    $ function just {
    >   command just --list --list-heading '' --list-prefix '' 2>/dev/null | awk '{print $1, substr($0, index($0, "#"))}'
    > }
-->

    $ just
    check # Invoke all checks (lints, tests, readme)
    check-wheel # Check that the wheel we build works in a completely empty venv (i.e. check for unspecified dependencies)
    clean # Clean all gitignored files/directories
    dist # Build distribution artifacts (tar, wheel)
    help # Display this help
    ipython # Invoke IPython in venv (not installed by default)
    lint # Invoke lints
    lint-flake8 # Run flake8
    lint-isort # Run isort check
    lint-mypy # Run mypy
    pipx # Install locally using pipx
    pipx-site-packages # Install locally using pipx (--system-site-packages)
    readme # Update usage/examples in *.md and fail if it differs from version control
    template-merge # Re-render cookiecutter template and merge into the current branch
    template-update # Re-render cookiecutter template into the template branch
    test # Invoke tests
    test-prysk # Run prysk tests
    test-pytest # Run pytest
    twine-upload # Release to PyPI
    venv # Setup ./.venv/
    venv-system-site-packages # Setup ./.venv/ (--system-site-packages)
<!-- end include tests/readme/make-help.md -->

[ci]: https://github.com/liskin/strava-offline/actions

## Style Guidelines

* Try to follow the existing style (where it's not already enforced by a
  linter). This applies to both code and git commits.

* Familiarise yourself with [the seven rules of a great Git commit
  message](https://cbea.ms/git-commit/#seven-rules).
