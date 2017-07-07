#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages
# from ??? import find_package_data


PACKAGE = "MyDB"
NAME = "MyDB"
DESCRIPTION = "A simple MySQL connection for thread web request and sql query maker"
AUTHOR = "icersong"
AUTHOR_EMAIL = "icersong@gmail.com"
URL = ""
#  VERSION = __import__(PACKAGE).__version__
VERSION = '1.4'

#  print find_packages(exclude=["tests.*", "tests", "scripts"])
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.rst").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL",
    url=URL,
    packages=find_packages(exclude=["tests.*", "tests", "scripts"]),
    install_requires=['mysql-python'],
    #  package_data=find_package_data(
    #      PACKAGE,
    #      only_in_packages=False
    #  ),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GPL License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: None",
    ],
    platforms=['any'],
    zip_safe=False,
)
