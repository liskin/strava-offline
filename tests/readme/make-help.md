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
