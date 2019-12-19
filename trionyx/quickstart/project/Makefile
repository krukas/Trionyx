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
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt



first_setup: setup
	@( \
		. env/bin/activate; \
		python manage.py migrate; \
		python manage.py createcachetable; \
		echo ""; \
		echo "Create super user:"; \
		python manage.py createsuperuser; \
		echo ""; \
		echo -e "\033[32m Setup complete, to start the development server use\033[33m make run"; \
		echo ""; \
	)



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
		celery worker -A celery_app -B -l info; \
	)



lint:
	-$(FLAKE8) apps
	-$(PYDOCSTYLE) apps



test: lint
	$(COVERAGE) run manage.py test



locales_collect:
	@( \
	    . env/bin/activate; \
	    python manage.py makemessages -l 'en_US' -i 'env/*' --no-obsolete; \
	    python manage.py makemessages -l 'nl_NL' -i 'env/*' --no-obsolete; \
    )



locales_compile:
	@(. env/bin/activate; python manage.py compilemessages -l en_US -l nl_NL)