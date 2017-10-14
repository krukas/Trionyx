PIP := env/bin/pip
PY := env/bin/python
FLAKE8 := env/bin/flake8
PYDOCSTYLE := env/bin/pydocstyle


help:
	@echo "COMMANDS:"
	@echo "  clean          Remove all generated files."
	@echo "  setup          Setup development environment."
	@echo "  shell          Open ipython from the development environment."
	@echo "  test           Run tests."
	@echo ""



clean:
	rm -rf env
	rm -rf build
	rm -rf dist
	rm -rf *.egg
	rm -rf *.egg-info
	find | grep -i ".*\.pyc$$" | xargs -r -L1 rm



virtualenv: clean
	virtualenv -p python3 env



setup: virtualenv
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt



shell:
	@( \
		. env/bin/activate; \
		python manage.py shell; \
	)


run:
	@( \
		. env/bin/activate; \
		python manage.py runserver; \
	)



lint:
	-$(FLAKE8) trionyx
	-$(PYDOCSTYLE) trionyx
	-$(FLAKE8) tests
	-$(PYDOCSTYLE) tests



test: lint
	$(PY) tests/run_tests.py
