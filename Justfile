set shell := ["bash", "-eu", "-o", "pipefail", "-c"]
set script-interpreter := ["bash", "-eux", "-o", "pipefail"]

venv_include_system_site_packages := shell("grep -s -l '^include-system-site-packages\\s*=\\s*true$' .venv/pyvenv.cfg || :")
uv_run_sync_flags := if venv_include_system_site_packages == "" { '--exact --all-extras' } else { '--no-sync' }
# ^ uv's dependency solver ignores --system-site-packages, so we need to pass --no-sync

# ----------------------------------------------------------------------

help:
    @just --list --unsorted

# Run all checks (`lint`, `test`, `readme-diff`)
check: lint test readme-diff

# Clean all gitignored files/directories
clean:
    git clean -ffdX

# Invoke IPython with the project and its dependencies available
ipython:
    uv run {{ uv_run_sync_flags }} --with ipython python -m IPython

# ----------------------------------------------------------------------

lint_sources := 'src/ tests/'
readme_sources := './*.md'

# Run all linters
[group('check')]
lint: lint-flake8 lint-mypy lint-isort

[group('check')]
lint-flake8:
    uv run {{ uv_run_sync_flags }} python -m flake8 {{ lint_sources }}

[group('check')]
lint-mypy:
    uv run {{ uv_run_sync_flags }} python -m mypy --show-column-numbers {{ lint_sources }}

[group('check')]
lint-isort:
    uv run {{ uv_run_sync_flags }} python -m isort --check {{ lint_sources }}

# Run all tests
[group('check')]
test: test-pytest test-prysk

# Run Python tests
[group('check')]
test-pytest *pytest_flags:
    uv run {{ uv_run_sync_flags }} python -m pytest {{ pytest_flags }} tests/

# Run CLI tests
[group('check')]
test-prysk *prysk_flags=shell("[ -t 0 ] && echo --interactive || :"):
    shopt -s nullglob && \
    uv run {{ uv_run_sync_flags }} python -m prysk --indent=4 --shell=/bin/bash {{ prysk_flags }} tests/*.md tests/*/*.md tests/*/*/*.md

# Update usage/examples in docs
[group('check')]
readme: test-prysk
    uv run {{ uv_run_sync_flags }} python tests/include-preproc.py --comment-start="<!-- " --comment-end=" -->" {{ readme_sources }}

# `readme` and fail if they differ from version control
[group('check')]
readme-diff: readme
    git diff --exit-code {{ readme_sources }}

# ----------------------------------------------------------------------

# Build distribution artifacts (sdist, wheel)
[group('dist')]
dist:
    uv build --clear

# Publish to PyPI
[group('dist')]
publish: dist
    uv publish

# Smoke test the build artifacts in an isolated venv (i.e. check for unspecified dependencies)
[group('dist')]
[script]
smoke-dist: dist
    package=$(uvx --from yq -- tomlq -e -r '.project.name | gsub("-"; "_")' pyproject.toml)
    for dist in dist/"$package"-*.{whl,tar*}; do
        for bin in $(uvx --from yq -- tomlq -e -r '.project.scripts | keys[]' pyproject.toml); do
            uv run \
                --isolated --no-project \
                --with "$dist" \
                -- "$bin" --help
        done
    done

# ----------------------------------------------------------------------

# Sync uv .venv
[group('venv')]
venv:
    uv sync {{ uv_run_sync_flags }}

# Setup .venv with --resolution lowest-direct (to test lower bounds of dependencies)
[group('venv')]
venv-lowest-direct:
    uv sync --resolution lowest-direct --all-extras

# Setup .venv with --system-site-packages
[group('venv')]
[script]
venv-system-site-packages:
    uv venv --system-site-packages --seed .venv
    extras=$(uvx --from yq -- tomlq -e -r '.project."optional-dependencies" // [] | keys | join(",")' pyproject.toml)
    uv run --no-sync python -m pip install --group dev -e ".[ $extras ]"
    # ^ uv's dependency solver ignores --system-site-packages, so we need to use pip

# ----------------------------------------------------------------------

template := 'cookiecutter-python-cli'
templates_dir := home_directory() / 'src'

# Re-render cookiecutter template into the template branch
[group('template')]
template-update:
    {{ templates_dir / template }}/update.sh \
        -t {{ shell('realpath --relative-to=. "$1"', templates_dir / template) }} \
        -p . \
        -b template \
        -i .cookiecutter.json

# `template-update` and merge into the current branch
[group('template')]
template-merge: template-update
    git merge template
