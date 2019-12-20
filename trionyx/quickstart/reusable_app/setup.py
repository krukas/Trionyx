from setuptools import setup
from setuptools import find_packages
from [[name]] import __version__


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name = '[[name]]',
    packages = find_packages(include=['[[name]]', '[[name]].*']),
    include_package_data=True,
    version = __version__,
    description = '[[name]]',
    long_description=readme(),
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
    license='GPL3',
    python_requires='~=3.6',
    install_requires=[],
    extras_require={
        'dev': [
            'Trionyx',
            'colorlog',
            'django-extensions',
            'django-debug-toolbar',
            'Werkzeug',
            'coverage',
            'flake8',
            'pydocstyle',
            'ipython',
        ]
    },
    entry_points={
        'trionyx.app': [
            '[[name]]=[[name]]',
        ],
    }
)
