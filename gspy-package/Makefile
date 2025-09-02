.PHONY: help clean clean-build clean-pyc clean-test lint test test-all coverage dist release install install-dev servedocs

.DEFAULT_GOAL := help

# ---- Configuration ----
PY      ?= python3
PACKAGE ?= gspy_egse
TESTS   ?= tests
DISTDIR ?= dist

# Optional: browser opener used by the 'coverage' target
define BROWSER_PYSCRIPT
import os, webbrowser, sys
from urllib.request import pathname2url
webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := $(PY) -c "$$BROWSER_PYSCRIPT"

# Pretty help from '##' comments
define PRINT_HELP_PYSCRIPT
import re, sys
for line in sys.stdin:
    m = re.match(r'^([a-zA-Z0-9_/-]+):.*?## (.*)$$', line)
    if m:
        target, help = m.groups()
        print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help: ## show this help
	@$(PY) -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

# ---- Cleaning ----
clean: clean-build clean-pyc clean-test ## remove build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -rf build/ $(DISTDIR)/ .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python bytecode and caches
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~'   -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test: ## remove test and coverage artifacts
	rm -rf .tox/ .pytest_cache/ htmlcov/
	rm -f .coverage

# ---- Quality / Tests ----
lint: ## run flake8 on package and tests
	flake8 $(PACKAGE) $(TESTS)

test: ## run tests with pytest
	pytest

test-all: ## run tests with tox (all environments)
	tox

coverage: ## run coverage and open HTML report
	$(PY) -m coverage run --source $(PACKAGE) -m pytest
	$(PY) -m coverage report -m
	$(PY) -m coverage html
	$(BROWSER) htmlcov/index.html

# ---- Docs (optional) ----
# If you revive Sphinx docs later, uncomment and adjust:
# docs: ## build Sphinx docs
# 	$(MAKE) -C docs clean
# 	$(MAKE) -C docs html
# 	$(BROWSER) docs/_build/html/index.html
#
# servedocs: docs ## rebuild docs on changes (requires watchdog)
# 	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

# ---- Packaging / Release ----
dist: clean ## build sdist and wheel (requires: pip install build)
	$(PY) -m build
	ls -l $(DISTDIR)

release: dist ## upload to PyPI (requires: pip install twine)
	twine upload $(DISTDIR)/*

# ---- Installation ----
install: clean ## install the package (non-editable)
	$(PY) -m pip install .

install-dev: clean ## install in editable mode for development
	$(PY) -m pip install -e .
	@echo "Editable install done. If you have dev extras, use: '$(PY) -m pip install -e .[dev]'"
