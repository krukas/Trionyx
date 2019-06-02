from setuptools import setup
from setuptools import find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name = 'Trionyx',
    packages = find_packages(exclude=['app']),
    include_package_data=True,
    scripts=['trionyx/bin/trionyx'],
    version = '0.1.1',
    description = 'Trionyx is an application framework for managing data and processes',
    long_description=readme(),
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'Topic :: Office/Business :: Groupware',

    ],
    author = 'Maikel Martens',
    author_email = 'maikel@martens.me',
    license='GPL3',
    url = 'https://github.com/krukas/Trionyx',
    download_url = 'https://github.com/krukas/Trionyx/releases/tag/0.1.1',
    keywords = ['Django', 'Trionyx', 'framework', 'admin', 'data', 'processes', 'application', 'stack'],
    install_requires=[
        "Django >= 2.2.0, < 2.3",

        # Django apps
        'django-crispy-forms >= 1.7.2, < 1.8',
        'django_compressor >= 2.3.0, < 2.4',
        'django_jsend==0.4',
        'jsonfield2==3.0.2',
        'django-watson >= 1.5.0, < 1.6',

        'Babel >= 2.6.0, < 2.7',

        'celery >= 4.3.0, < 4.4',

        'Pillow==6.0.0',
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
            'ipython',
            'Sphinx',
            'sphinx_rtd_theme',
        ]
    }
)

