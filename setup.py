#!/usr/bin/env python

from setuptools import setup, find_packages
from sniffer import __version__, __author__, __author_email__

setup(
    name='sniffer',
    version=__version__,
    description='An automatic nose test runner.',
    long_description=open('README.txt').read(),
    author=__author__,
    author_email=__author_email__,
    url='http://github.com/jeffh/sniffer/',
    requires=['nose'],
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
    ],
)
