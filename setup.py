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
	version = '0.1.2',
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
	download_url = 'https://github.com/krukas/Trionyx/releases/tag/0.1.2',
	keywords = ['Django', 'Trionyx', 'framework', 'admin', 'data', 'processes', 'application', 'stack'],
	install_requires=[
        "Django >= 1.11.0, < 1.12",

		# Django apps
		'django-crispy-forms >= 1.7.2, < 1.8',
		'django_compressor >= 2.2.0, < 2.3',
		'django_jsend==0.4',
		'jsonfield==2.0.2',
		'django-watson >= 1.5.0, < 1.6',

		'Babel >= 2.5.3, < 2.6',

		'celery >= 4.1.0, < 4.2',

		'Pillow==5.0.0',
    ],
)

