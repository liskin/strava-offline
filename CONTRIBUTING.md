# Contributing to strava-offline

## Development

Obtain the source code:

    $ git clone https://github.com/liskin/strava-offline

Setup Python virtual env and install dependencies:

    $ just venv

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
-->

    $ just help
    Available recipes:
        help
        check                     # Run all checks (`lint`, `test`, `readme-diff`)
        clean                     # Clean all gitignored files/directories
        ipython                   # Invoke IPython with the project and its dependencies available
    
        [check]
        lint                      # Run all linters
        lint-flake8
        lint-mypy
        lint-isort
        test                      # Run all tests
        test-pytest *pytest_flags # Run Python tests
        test-prysk *prysk_flags=shell("[ -t 0 ] && echo --interactive || :") # Run CLI tests
        readme                    # Update usage/examples in docs
        readme-diff               # `readme` and fail if they differ from version control
    
        [dist]
        dist                      # Build distribution artifacts (sdist, wheel)
        publish                   # Publish to PyPI
        smoke-dist                # Smoke test the build artifacts in an isolated venv (i.e. check for unspecified dependencies)
    
        [venv]
        venv                      # Sync uv .venv
        venv-system-site-packages # Setup .venv with --system-site-packages
    
        [template]
        template-update           # Re-render cookiecutter template into the template branch
        template-merge            # `template-update` and merge into the current branch
<!-- end include tests/readme/make-help.md -->

[ci]: https://github.com/liskin/strava-offline/actions

## Style Guidelines

* Try to follow the existing style (where it's not already enforced by a
  linter). This applies to both code and git commits.

* Familiarise yourself with [the seven rules of a great Git commit
  message](https://cbea.ms/git-commit/#seven-rules).
