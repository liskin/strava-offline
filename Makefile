SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

UV_RUN_SYNC_FLAGS ?= --exact --all-extras

.PHONY: check
## Invoke all checks (lints, tests, readme)
check: lint test readme

.PHONY: lint
## Invoke lints
lint: lint-flake8 lint-mypy lint-isort

LINT_SOURCES = src/ tests/

.PHONY: lint-flake8
##
lint-flake8:
	uv run $(UV_RUN_SYNC_FLAGS) python -m flake8 $(LINT_SOURCES)

.PHONY: lint-mypy
##
lint-mypy:
	uv run $(UV_RUN_SYNC_FLAGS) python -m mypy --show-column-numbers $(LINT_SOURCES)

.PHONY: lint-isort
##
lint-isort:
	uv run $(UV_RUN_SYNC_FLAGS) python -m isort --check $(LINT_SOURCES)

.PHONY: test
## Invoke tests
test: test-pytest test-prysk

.PHONY: test-pytest
##
test-pytest:
	uv run $(UV_RUN_SYNC_FLAGS) python -m pytest $(PYTEST_FLAGS) tests/

.PHONY: test-prysk
##
test-prysk: PRYSK_INTERACTIVE := $(shell [ -t 0 ] && echo --interactive)
test-prysk:
	uv run $(UV_RUN_SYNC_FLAGS) python -m prysk --indent=4 --shell=/bin/bash $(PRYSK_INTERACTIVE) \
		$(wildcard tests/*.md tests/*/*.md tests/*/*/*.md)

.PHONY: readme
## Update usage/examples in *.md and fail if it differs from version control
readme: $(wildcard *.md)
	git diff --exit-code $^

.PHONY: $(wildcard *.md)
$(wildcard *.md) &: test-prysk
	uv run $(UV_RUN_SYNC_FLAGS) python tests/include-preproc.py --comment-start="<!-- " --comment-end=" -->" $(wildcard *.md)

.PHONY: dist
## Build distribution artifacts (sdist, wheel)
dist:
	uv build --clear

.PHONY: publish
## Publish to PyPI
publish: dist
	uv publish

.PHONY: ipython
## Invoke IPython with the project and its dependencies available
ipython:
	uv run $(UV_RUN_SYNC_FLAGS) --with ipython python -m IPython

.PHONY: clean
## Clean all gitignored files/directories
clean:
	git clean -ffdX

.PHONY: template-update
## Re-render cookiecutter template into the template branch
template-update: TEMPLATES_DIR ?= $(HOME)/src
template-update: TEMPLATE := $(shell realpath --relative-to=. $(TEMPLATES_DIR)/cookiecutter-python-cli)
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

.PHONY: venv
## Sync uv venv
venv:
	uv sync $(UV_RUN_SYNC_FLAGS)

.PHONY: venv-system-site-packages
## Setup $(VENV) (--system-site-packages)
venv-system-site-packages: UV_RUN_SYNC_FLAGS=--no-sync
venv-system-site-packages:
	uv venv --system-site-packages --seed .venv
	extras=$$(uvx --from yq -- tomlq -e -r '.project."optional-dependencies" // [] | keys | join(",")' pyproject.toml); \
	uv run $(UV_RUN_SYNC_FLAGS) python -m pip install --group dev -e ".[ $$extras ]"
	@echo
	@echo "Now use: make UV_RUN_SYNC_FLAGS=$(UV_RUN_SYNC_FLAGS)"
	@if [[ $${GITHUB_ENV-} ]]; then echo 'UV_RUN_SYNC_FLAGS="$(UV_RUN_SYNC_FLAGS)"' >> $$GITHUB_ENV; fi
# ^ uv's dependency solver ignores --system-site-packages, so we need to use pip

include _help.mk
