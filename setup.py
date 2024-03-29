#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from setuptools import find_packages, setup

import versioneer

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
    author="Data Revenue GmbH",
    author_email='alan@datarevenue.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='drfs',
    name='drfs',
    packages=find_packages(exclude=['drfs.tests.*', 'drfs.tests', 'examples']),
    url='https://github.com/datarevenue-berlin/drfs',
    version = versioneer.get_version(),
    cmdclass = versioneer.get_cmdclass(),
    zip_safe=False,
)
