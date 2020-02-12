PY_VERSION := python3
PIP := env/bin/pip
PY := env/bin/python
FLAKE8 := env/bin/flake8
PYDOCSTYLE := env/bin/pydocstyle
COVERAGE := env/bin/coverage


help:
	@echo "COMMANDS:"
	@echo "  clean              Remove all generated files."
	@echo "  setup              Setup development environment."
	@echo "  shell              Open ipython from the development environment."
	@echo "  test               Run tests."
	@echo "  run                Start development server"
	@echo "  celery             Start celery"
	@echo "  locales_collect    Collect all translation"
	@echo "  locales_compile    Compile all translation"
	@echo ""



clean:
	rm -rf env
	rm -rf build
	rm -rf dist
	rm -rf *.egg
	rm -rf *.egg-info
	find | grep -i ".*\.pyc$$" | xargs -r -L1 rm



virtualenv: clean
	$(PY_VERSION) -m venv env



setup: virtualenv
	$(PIP) install -e .
	$(PIP) install -e .[dev]



shell:
	@( \
		. env/bin/activate; \
		python manage.py shell_plus; \
	)



lint:
	-$(FLAKE8) trionyx_accounts
	-$(PYDOCSTYLE) trionyx_accounts



test: lint
	$(COVERAGE) run manage.py test tests



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



locales_update:
	@( \
	    . env/bin/activate; \
	    $(PY) manage.py makemessages -l 'en_US' -i 'env/*' --no-obsolete; \
	    $(PY) manage.py makemessages -l 'nl_NL' -i 'env/*' --no-obsolete; \
    )


locales_compile:
	@(. env/bin/activate; $(PY) manage.py compilemessages -l en_US -l nl_NL)