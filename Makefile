SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

PYTHON = python3

VENV = .venv
VENV_PYTHON = $(VENV)/bin/python
VENV_DONE = $(VENV)/.done
VENV_SYSTEM_SITE_PACKAGES = $(VENV)/.venv-system-site-packages
VENV_USE_SYSTEM_SITE_PACKAGES = $(wildcard $(VENV_SYSTEM_SITE_PACKAGES))

TEMPLATES_DIR = $(HOME)/src
TEMPLATE = $(eval TEMPLATE := $$(shell realpath --relative-to=. $$(TEMPLATES_DIR)/cookiecutter-python-cli))$(TEMPLATE)

.PHONY: venv-system-site-packages
## Setup ./.venv/ (--system-site-packages)
venv-system-site-packages:
	$(MAKE) VENV_USE_SYSTEM_SITE_PACKAGES=1 venv

.PHONY: venv
## Setup ./.venv/
venv: $(VENV_DONE)

.PHONY: check
## Invoke all checks (lints, tests, readme)
check: lint test readme

.PHONY: lint
## Invoke lints
lint: lint-flake8 lint-mypy lint-isort

LINT_SOURCES = src/ tests/

.PHONY: lint-flake8
##
lint-flake8: $(VENV_DONE)
	$(VENV_PYTHON) -m flake8 $(LINT_SOURCES)

.PHONY: lint-mypy
##
lint-mypy: $(VENV_DONE)
	$(VENV_PYTHON) -m mypy --show-column-numbers $(LINT_SOURCES)

.PHONY: lint-isort
##
lint-isort: $(VENV_DONE)
	$(VENV_PYTHON) -m isort --check $(LINT_SOURCES)

.PHONY: test
## Invoke tests
test: test-pytest test-prysk

.PHONY: test-pytest
##
test-pytest: $(VENV_DONE)
	$(VENV_PYTHON) -m pytest $(PYTEST_FLAGS) tests/

.PHONY: test-prysk
##
test-prysk: PRYSK_INTERACTIVE=$(shell [ -t 0 ] && echo --interactive)
test-prysk: $(VENV_DONE)
	PATH="$(CURDIR)/$(VENV)/bin:$$PATH" \
	XDG_DATA_HOME=/home/user/.local/share \
	XDG_CONFIG_HOME=/home/user/.config \
	$(VENV_PYTHON) -m prysk --indent=4 --shell=/bin/bash $(PRYSK_INTERACTIVE) \
		$(wildcard tests/*.md tests/*/*.md tests/*/*/*.md)

.PHONY: readme
## Update usage/examples in *.md and fail if it differs from version control
readme: $(wildcard *.md)
	git diff --exit-code $^

.PHONY: $(wildcard *.md)
$(wildcard *.md) &: $(VENV_DONE) test-prysk
	$(VENV_PYTHON) tests/include-preproc.py --comment-start="<!-- " --comment-end=" -->" $(wildcard *.md)

.PHONY: dist
## Build distribution artifacts (sdist, wheel)
dist:
	uv build --clear

.PHONY: publish
## Publish to PyPI
publish: dist
	uv publish

.PHONY: ipython
## Invoke IPython in venv (not installed by default)
ipython: $(VENV_DONE)
	$(VENV_PYTHON) -m IPython

.PHONY: clean
## Clean all gitignored files/directories
clean:
	git clean -ffdX

.PHONY: template-update
## Re-render cookiecutter template into the template branch
template-update:
	$(TEMPLATE)/update.sh -t $(TEMPLATE) -p . -b template -i .cookiecutter.json

.PHONY: template-merge
## Re-render cookiecutter template and merge into the current branch
template-merge: template-update
	git merge template

.PHONY: smoke-dist
## Smoke test the build artifacts in an isolated venv
## (i.e. check for unspecified dependencies)
smoke-dist: dist
	package=$$(uvx --from yq -- tomlq -e -r '.project.name | gsub("-"; "_")' pyproject.toml); \
	for dist in dist/"$$package"-*.{whl,tar*}; do \
		uv run \
			--isolated --no-project \
			--with "$$dist" \
			-- python -m "$$package" --help; \
	done

define VENV_CREATE
	$(PYTHON) -m venv $(VENV)
endef

define VENV_CREATE_SYSTEM_SITE_PACKAGES
	$(PYTHON) -m venv --system-site-packages --without-pip $(VENV)
	touch $(VENV_SYSTEM_SITE_PACKAGES)
endef

$(VENV_DONE): $(MAKEFILE_LIST) pyproject.toml
	$(if $(VENV_USE_SYSTEM_SITE_PACKAGES),$(VENV_CREATE_SYSTEM_SITE_PACKAGES),$(VENV_CREATE))
	$(VENV_PYTHON) -m pip install 'pip >= 25.1' # PEP-735 (dependency groups)
	extras=$$(uvx --from yq -- tomlq -e -r '.project."optional-dependencies" // [] | keys | join(",")' pyproject.toml); \
	$(VENV_PYTHON) -m pip install --group dev -e ".[ $$extras ]"
	touch $@

include _help.mk
