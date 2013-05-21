#!/usr/bin/env python
from setuptools import setup, find_packages

VERSION = __import__('usertools').__version__

setup(
    name="usertools",
    version=VERSION,
    author='Siddharth Doshi',
    author_email='scdoshi@gmail.com',
    description=("Extras for Django Auth and User Management"),
    packages=find_packages(),
    url="http://github.com/scdoshi/django-usertools/",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
