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
	version = '0.0.1',
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
	download_url = 'https://github.com/krukas/Trionyx/releases/tag/0.0.1',
	keywords = ['Django', 'Trionyx', 'framework', 'admin', 'data', 'processes', 'application'],
	install_requires=[
        "Django >= 1.11.0, < 1.12",
        "djangorestframework >= 3.6.0, < 3.7",
        "djangorestframework-jwt >= 1.11, < 2.0",
        "django-cors-headers >= 2.1, < 3.0",
    ],
)
