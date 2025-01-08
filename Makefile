.PHONY: help
help:
	@echo "Targets:"
	@echo "  help:  	  Show this page"
	@echo ""
	@echo "  all:         pre-commit + test + doc"
	@echo ""
	@echo "  pre-commit:  Run pre-commit fixes and checks"
	@echo "  test:        Run pytest"
	@echo "  doc:         Build Documentation"
	@echo ""
	@echo "  clean:       All Temporary Files (from .gitignore)"
	@echo ""

.PHONY: all
all: pre-commit test doc

.PHONY: pre-commit
pre-commit: .venv/.sync
	uv run pre-commit run --all-files

.PHONY: test
test: .venv/.sync
	uv run coverage run --source=anycache --branch -m pytest --doctest-glob=docs/*.rst --doctest-modules --ignore-glob=tests/testdata* --ignore=docs/conf.py --log-level=DEBUG -vv --junitxml=report.xml
	uv run coverage report
	uv run coverage html
	uv run coverage xml

.PHONY: doc
doc: .venv/.sync
	uv run make html -C docs

.PHONY: clean
clean:
	git clean -Xdf

.venv/.sync:
	uv sync --dev
