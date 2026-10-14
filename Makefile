LAB ?=
TASK ?=
ARGS ?=
COVERAGE_MIN ?= 80
PYTHON ?= python3

CI_EXTRA :=

PRE_COMMIT_CONFIG := .config/.pre-commit-config.yaml

export PYTHONPYCACHEPREFIX := $(CURDIR)/build/pycache

-include .config/local.mk

.DEFAULT_GOAL := help

.PHONY: help setup test run format lint typecheck coverage ci clean

help:
	@echo "make run      LAB=labN [TASK=taskN] [ARGS=]  run labN/main.py (all tasks) or labN/taskN/main.py"
	@echo "make test     [LAB=labN]                  run tests"
	@echo "make format                               apply all formatters"
	@echo "make lint                                 pre-commit hooks and mypy"
	@echo "make coverage [COVERAGE_MIN=80]           line coverage gate"
	@echo "make ci                                   everything CI runs"
	@echo "make clean                                remove build outputs"

setup:
	pre-commit install -c $(PRE_COMMIT_CONFIG)

test:
	$(PYTHON) -m pytest $(LAB)

run:
	@test -n "$(LAB)" || (echo "LAB is required" >&2; exit 2)
	@$(PYTHON) -m $(LAB).$(if $(filter-out all,$(TASK)),$(TASK).)main $(ARGS)

format:
	-pre-commit run -c $(PRE_COMMIT_CONFIG) --all-files

lint:
	pre-commit run -c $(PRE_COMMIT_CONFIG) --all-files --show-diff-on-failure
	$(MAKE) typecheck

typecheck:
	$(PYTHON) -m mypy

coverage:
	mkdir -p build/artifacts/coverage
	$(PYTHON) -m pytest --cov --cov-report=term-missing \
		--cov-report=html:build/artifacts/coverage --cov-fail-under=$(COVERAGE_MIN)

ci: lint coverage $(CI_EXTRA)

clean:
	rm -rf build
