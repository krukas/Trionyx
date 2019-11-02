PIP := env/bin/pip
PY := env/bin/python
FLAKE8 := env/bin/flake8
MYPY := env/bin/mypy
PYDOCSTYLE := env/bin/pydocstyle
COVERAGE := env/bin/coverage


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
	$(PIP) install -e .
	$(PIP) install -e .[dev]



shell:
	@( \
		. env/bin/activate; \
		python manage.py shell_plus; \
	)


run:
	@( \
		. env/bin/activate; \
		python manage.py runserver_plus; \
	)



celery:
	@( \
		. env/bin/activate; \
		celery worker -A app.celery -B -l info; \
	)



lint:
	-$(FLAKE8) trionyx
	-$(PYDOCSTYLE) trionyx
	-$(FLAKE8) tests
	-$(MYPY)



test: lint
	$(COVERAGE) run manage.py test tests



locales_update:
	@( \
	    . env/bin/activate; \
	    python$(PY_VERSION) manage.py makemessages -l 'en_US' -i 'env/*' --no-obsolete; \
	    python$(PY_VERSION) manage.py makemessages -l 'nl_NL' -i 'env/*' --no-obsolete; \
    )


locales_compile:
	@(. env/bin/activate; python$(PY_VERSION) manage.py compilemessages -l en_US -l nl_NL)