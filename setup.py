#!/usr/bin/env python

from setuptools import find_packages, setup

description = ('Utilities for benchmarking python code.')

# Read in requirements
requirements = [
    requirement.strip() for requirement in open('requirements.txt').readlines()
]

setup(
    name='benchmarkutils',
    version='0.0.1',
    author_email='martin.ganahl@gmail.com',
    python_requires=('>=3.7.0'),
    install_requires=requirements,
    description=description,
    packages=find_packages(),
)
