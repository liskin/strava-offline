PYTHON := "python3"

VENV := ".venv"
VENV_PYTHON := VENV + "/bin/python"
VENV_DONE := VENV + "/.done"
VENV_PIP_INSTALL := '.[dev, test]'
VENV_SYSTEM_SITE_PACKAGES := VENV + "/.venv-system-site-packages"

VENV_WHEEL := ".venv-wheel"
VENV_WHEEL_PYTHON := VENV_WHEEL + "/bin/python"

LINT_SOURCES := "src/ tests/"

# Display this help
help:
    @just --list

# Setup ./.venv/ (--system-site-packages)
venv-system-site-packages: (_venv "1")

# Setup ./.venv/
venv: (_venv "")

# Internal recipe to create venv
_venv use_system="":
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -f "{{VENV_DONE}}" ]; then
        # Check if pyproject.toml or Justfile are newer than the venv
        if [ "pyproject.toml" -nt "{{VENV_DONE}}" ] || [ "Justfile" -nt "{{VENV_DONE}}" ]; then
            rm -f "{{VENV_DONE}}"
        else
            exit 0
        fi
    fi
    
    if [ "{{use_system}}" = "1" ]; then
        # Create venv with system site packages
        {{PYTHON}} -m venv --system-site-packages --without-pip {{VENV}} || true
        {{VENV_PYTHON}} -m pip --version || {{PYTHON}} -m venv --system-site-packages {{VENV}}
        {{VENV_PYTHON}} -m pip install 'pip >= 22.3'
        touch {{VENV_SYSTEM_SITE_PACKAGES}}
        
        # Apply Debian workaround if needed
        if [ -f /etc/debian_version ] && {{PYTHON}} -c 'import sys; exit(not(sys.version_info < (3, 10)))' 2>/dev/null; then
            export SETUPTOOLS_USE_DISTUTILS=stdlib
        fi
    else
        # Create regular venv
        {{PYTHON}} -m venv {{VENV}}
    fi
    
    {{VENV_PYTHON}} -m pip install -e '{{VENV_PIP_INSTALL}}'
    touch {{VENV_DONE}}

# Install locally using pipx
pipx:
    pipx install --editable .

# Install locally using pipx (--system-site-packages)
pipx-site-packages:
    pipx install --system-site-packages --editable .

# Invoke all checks (lints, tests, readme)
check: lint test readme

# Invoke lints
lint: lint-flake8 lint-mypy lint-isort

# Run flake8
lint-flake8: (_venv "")
    {{VENV_PYTHON}} -m flake8 {{LINT_SOURCES}}

# Run mypy
lint-mypy: (_venv "")
    {{VENV_PYTHON}} -m mypy --show-column-numbers {{LINT_SOURCES}}

# Run isort check
lint-isort: (_venv "")
    {{VENV_PYTHON}} -m isort --check {{LINT_SOURCES}}

# Invoke tests
test: test-pytest test-prysk

# Run pytest
test-pytest: (_venv "")
    {{VENV_PYTHON}} -m pytest ${PYTEST_FLAGS:-} tests/

# Run prysk tests
test-prysk: (_venv "")
    #!/usr/bin/env bash
    set -euo pipefail
    PRYSK_INTERACTIVE=""
    if [ -t 0 ]; then
        PRYSK_INTERACTIVE="--interactive"
    fi
    PATH="$(pwd)/{{VENV}}/bin:$PATH" \
    XDG_DATA_HOME=/home/user/.local/share \
    XDG_CONFIG_HOME=/home/user/.config \
    {{VENV_PYTHON}} -m prysk --indent=4 --shell=/bin/bash $PRYSK_INTERACTIVE \
        tests/*.md tests/*/*.md tests/*/*/*.md 2>/dev/null || true

# Update usage/examples in *.md and fail if it differs from version control
readme: (_update-readme "README.md") (_update-readme "CONTRIBUTING.md")
    git diff --exit-code README.md CONTRIBUTING.md

# Internal recipe to update a readme file
_update-readme file: (_venv "") test-prysk
    {{VENV_PYTHON}} tests/include-preproc.py --comment-start="<!-- " --comment-end=" -->" {{file}}

# Build distribution artifacts (tar, wheel)
dist: (_venv "")
    rm -rf dist/
    {{VENV_PYTHON}} -m build --outdir dist

# Release to PyPI
twine-upload: dist
    {{VENV_PYTHON}} -m twine upload dist/*

# Invoke IPython in venv (not installed by default)
ipython: (_venv "")
    {{VENV_PYTHON}} -m IPython

# Clean all gitignored files/directories
clean:
    git clean -ffdX

# Re-render cookiecutter template into the template branch
template-update:
    #!/usr/bin/env bash
    set -euo pipefail
    TEMPLATES_DIR="${HOME}/src"
    TEMPLATE=$(realpath --relative-to=. "${TEMPLATES_DIR}/cookiecutter-python-cli")
    "${TEMPLATE}/update.sh" -t "${TEMPLATE}" -p . -b template -i .cookiecutter.json

# Re-render cookiecutter template and merge into the current branch
template-merge: template-update
    git merge template

# Check that the wheel we build works in a completely empty venv (i.e. check for unspecified dependencies)
check-wheel: dist
    #!/usr/bin/env bash
    set -euo pipefail
    PACKAGE=$(sed -ne '/^name / { y/-/_/; s/^.*=\s*"\(.*\)"/\1/p }' pyproject.toml)
    {{PYTHON}} -m venv --clear --without-pip {{VENV_WHEEL}}
    cd {{VENV_WHEEL}} && {{PYTHON}} -m pip --isolated download pip
    set -- {{VENV_WHEEL}}/pip-*-py3-none-any.whl
    {{VENV_WHEEL_PYTHON}} "$1/pip" install dist/${PACKAGE}-*.whl
    {{VENV_WHEEL_PYTHON}} -m ${PACKAGE} --help
