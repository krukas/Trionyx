#!/usr/bin/env python3
from setuptools import setup
from setuptools import find_packages
from trionyx import __version__

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name = 'Trionyx',
    packages = find_packages(include=['trionyx', 'trionyx.*']),
    include_package_data=True,
    scripts=['trionyx/bin/trionyx'],
    version = __version__,
    description = 'Trionyx is an application framework for managing data and processes',
    long_description=readme(),
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
    author = 'Maikel Martens',
    author_email = 'maikel@martens.me',
    license='GPL3',
    url = 'https://github.com/krukas/Trionyx',
    download_url = 'https://github.com/krukas/Trionyx/releases/tag/{}'.format(__version__),
    keywords = ['Django', 'Trionyx', 'framework', 'admin', 'data', 'processes', 'application', 'stack'],
    python_requires='~=3.6',
    install_requires=[
        "Django >= 2.2.0, < 2.3",

        # Django apps
        'django-crispy-forms >= 1.7.2, < 1.8',
        'django_compressor >= 2.3.0, < 2.4',
        'jsonfield2==3.0.2',
        'django-watson >= 1.5.0, < 1.6',
        'djangorestframework >= 3.10.0, < 3.11',

        'Babel >= 2.6.0, < 2.7',

        'celery >= 4.3.0, < 4.4',

        'Pillow>=5.0.0',
        'PyYAML==5.2',
        'docutils>=0.14',
    ],
    extras_require={
        'dev': [
            'colorlog',
            'django-extensions',
            'django-debug-toolbar',
            'Werkzeug',
            'coverage',
            'flake8',
            'pydocstyle',
            'mypy==0.750',
            'django-stubs >= 1.3.0, < 1.4.0',
            'ipython',
            'Sphinx',
            'sphinx_rtd_theme',
        ]
    },
)
