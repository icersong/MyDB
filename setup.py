#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re, sys
import subprocess
from distutils.core import setup
from setuptools import find_packages


PACKAGE = "MyDB"
NAME = "MyDB"
DESCRIPTION = "A simple MySQL connection for thread web request and sql query maker"
AUTHOR = "icersong"
AUTHOR_EMAIL = "icersong@gmail.com"
URL = ""
#  VERSION = __import__(PACKAGE).__version__


def make_version():
    #  p = subprocess.Popen(['git', 'branch', '-vv'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = subprocess.Popen(['git', 'log', '--oneline', '--graph', '--decorate', '-n1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if err or not out:
        print err
        sys.exit()
    info = out.split('\n')[0]
    m = re.match('.*\(HEAD, tag: (?P<tag>[\w.!@#$%&*-+/]+)[^\(\)]*\).*$', info)
    if not m:
        print 'Current is not branche tag.'
        print 'Please do command:'
        print '    $ git tag <tagname>'
        print '    $ git checkout <tagname>'
        sys.exit()
    #  print m.groupdict()
    with open('VERSION', 'wb') as fp:
        fp.write(m.groupdict()['tag'])


if [x for x in ['bdist', 'sdist', 'bdist_egg', 'bdist_whl', 'upload'] if x in sys.argv]:
    make_version()

with open('VERSION', 'rb') as fp:
    VERSION = fp.read().split('\n')[0].strip()

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
    install_requires=['mysql-python', 'som-common'],
    package_data={
        '': ['*.txt', '*.rst', '*.md'],
        'MyDB': ['*.xml'],
    },
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
