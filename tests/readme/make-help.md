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
