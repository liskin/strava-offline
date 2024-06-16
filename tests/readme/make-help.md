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
