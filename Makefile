PYTHON ?= python

.PHONY: test unit_test perf_test coverage lint doc

test:
	$(PYTHON) -m pytest

unit_test:
	$(PYTHON) -m pytest -m "not perf"

perf_test:
	$(PYTHON) -m pytest -m perf -s

coverage:
	-$(PYTHON) -m coverage run -m pytest -m "not perf" -q --tb=no
	$(PYTHON) -m coverage report

lint:
	$(PYTHON) -m ruff check .

doc:
	$(PYTHON) -m pdoc --html --force --output-dir docs triangulator
