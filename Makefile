PYTHON = python3

VENV = .venv
VENV_PYTHON = $(VENV)/bin/python
VENV_DONE = $(VENV)/.done
VENV_PIP_INSTALL = '.[dev, test]'
VENV_SYSTEM_SITE_PACKAGES = $(VENV)/.venv-system-site-packages
VENV_USE_SYSTEM_SITE_PACKAGES = $(wildcard $(VENV_SYSTEM_SITE_PACKAGES))

VENV_WHEEL = .venv-wheel
VENV_WHEEL_PYTHON = $(VENV_WHEEL)/bin/python

PACKAGE := $(shell sed -ne '/^name / { y/-/_/; s/^.*=\s*"\(.*\)"/\1/p }' pyproject.toml)

TEMPLATES_DIR = $(HOME)/src
TEMPLATE = $(eval TEMPLATE := $$(shell realpath --relative-to=. $$(TEMPLATES_DIR)/cookiecutter-python-cli))$(TEMPLATE)

.PHONY: venv-system-site-packages
## Setup ./.venv/ (--system-site-packages)
venv-system-site-packages:
	$(MAKE) VENV_USE_SYSTEM_SITE_PACKAGES=1 venv

.PHONY: venv
## Setup ./.venv/
venv: $(VENV_DONE)

.PHONY: pipx
## Install locally using pipx
pipx:
	pipx install --editable .

.PHONY: pipx-site-packages
## Install locally using pipx (--system-site-packages)
pipx-site-packages:
	pipx install --system-site-packages --editable .

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
$(wildcard *.md): $(VENV_DONE) test-prysk
	$(VENV_PYTHON) tests/include-preproc.py --comment-start="<!-- " --comment-end=" -->" $@

.PHONY: dist
## Build distribution artifacts (tar, wheel)
dist: $(VENV_DONE)
	rm -rf dist/
	$(VENV_PYTHON) -m build --outdir dist

.PHONY: twine-upload
## Release to PyPI
twine-upload: dist
	$(VENV_PYTHON) -m twine upload $(wildcard dist/*)

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

.PHONY: check-wheel
## Check that the wheel we build works in a completely empty venv
## (i.e. check for unspecified dependencies)
check-wheel: dist
	$(PYTHON) -m venv --clear --without-pip $(VENV_WHEEL)
	cd $(VENV_WHEEL) && $(PYTHON) -m pip --isolated download pip
	set -- $(VENV_WHEEL)/pip-*-py3-none-any.whl && $(VENV_WHEEL_PYTHON) $$1/pip install dist/$(PACKAGE)-*.whl
	$(VENV_WHEEL_PYTHON) -m $(PACKAGE) --help

define VENV_CREATE
	$(PYTHON) -m venv $(VENV)
endef

define VENV_CREATE_SYSTEM_SITE_PACKAGES
	$(PYTHON) -m venv --system-site-packages --without-pip $(VENV)
	$(VENV_PYTHON) -m pip --version || $(PYTHON) -m venv --system-site-packages $(VENV)
	$(VENV_PYTHON) -m pip install 'pip >= 22.3' # PEP-660 (editable without setup.py)
	touch $(VENV_SYSTEM_SITE_PACKAGES)
endef

# workaround for https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1003252 and/or https://github.com/pypa/pip/issues/6264
ifneq ($(VENV_USE_SYSTEM_SITE_PACKAGES),)
ifneq ($(shell test -f /etc/debian_version && python3 -c 'import sys; exit(not(sys.version_info < (3, 10)))' && echo x),)
$(warning XXX: using SETUPTOOLS_USE_DISTUTILS=stdlib workaround)
$(VENV_DONE): export SETUPTOOLS_USE_DISTUTILS := stdlib
endif
endif

$(VENV_DONE): $(MAKEFILE_LIST) pyproject.toml
	$(if $(VENV_USE_SYSTEM_SITE_PACKAGES),$(VENV_CREATE_SYSTEM_SITE_PACKAGES),$(VENV_CREATE))
	$(VENV_PYTHON) -m pip install -e $(VENV_PIP_INSTALL)
	touch $@

include _help.mk
