PYTHON = python3

VENV = .venv
VENV_PIP = $(VENV)/bin/pip
VENV_PYTHON = $(VENV)/bin/python
VENV_DONE = $(VENV)/.done
VENV_PIP_INSTALL = '.[dev, test]'

.PHONY: venv
venv: $(VENV_DONE)

.PHONY: venv-prod
venv-prod: override VENV_PIP_INSTALL = '.'
venv-prod: $(VENV_DONE)

.PHONY: dist
dist: $(VENV_DONE)
	$(VENV_PYTHON) setup.py sdist bdist_wheel

.PHONY: test
test: $(VENV_DONE)
	$(VENV_PY_TEST) $(pytest)

.PHONY: clean
clean:
	git clean -ffdX

$(VENV_DONE): $(MAKEFILE_LIST) setup.py $(wildcard *-requirements.txt)
	$(PYTHON) -m venv --system-site-packages $(VENV)
	$(VENV_PIP) install -r setup-requirements.txt
	$(VENV_PIP) install -e $(VENV_PIP_INSTALL)
	touch $@

# ---

.PHONY: yearly
yearly: YEAR=$(shell date +%Y)
yearly:
	m4 -DYEAR=$(YEAR) yearly_summary.sql.m4 \
		| sqlite3 strava.sqlite \
		| perl -0777 -pe 's/(SELECT.*?;)/`tput setaf 246` . $$1 . `tput sgr0`/gse'
