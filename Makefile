PYTHON = python3

VENV = .venv
VENV_PIP = $(VENV)/bin/pip
VENV_PYTHON = $(VENV)/bin/python
VENV_DONE = $(VENV)/.done
VENV_PIP_INSTALL = '.[dev, test]'

PACKAGE_SCRIPT = 'from configparser import RawConfigParser; p = RawConfigParser(); p.read("setup.cfg"); print(p["metadata"]["name"]);'
PACKAGE = $(shell $(PYTHON) -c $(PACKAGE_SCRIPT))

.PHONY: venv
venv: $(VENV_DONE)

.PHONY: pipx
pipx:
	pipx install --editable --spec . $(PACKAGE)

.PHONY: pipx-site-packages
pipx-site-packages:
	pipx install --system-site-packages --editable --spec . $(PACKAGE)

.PHONY: dist
dist: $(VENV_DONE)
	rm -rf dist/
	$(VENV_PYTHON) -m pep517.build --source --binary --out-dir dist .

.PHONY: twine-upload
twine-upload: dist
	$(VENV_PYTHON) -m twine upload $(wildcard dist/*)

.PHONY: clean
clean:
	git clean -ffdX

$(VENV_DONE): $(MAKEFILE_LIST) setup.py setup.cfg pyproject.toml
	$(PYTHON) -m venv --system-site-packages $(VENV)
	$(VENV_PIP) install -e $(VENV_PIP_INSTALL)
	touch $@

# ---

.PHONY: yearly
yearly: YEAR=$(shell date +%Y)
yearly:
	m4 -DYEAR=$(YEAR) yearly_summary.sql.m4 \
		| sqlite3 strava.sqlite \
		| perl -0777 -pe 's/(SELECT.*?;)/`tput setaf 246` . $$1 . `tput sgr0`/gse'
