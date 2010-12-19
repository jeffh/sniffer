from setuptools import setup, find_packages
from sniffer import __version__, __author__, __author_email__

setup(
    name='sniffer',
    version=__version__,
    description='An automatic test runner. Supports nose out of the box.',
    long_description=open('README.rst').read(),
    author=__author__,
    author_email=__author_email__,
    url='http://github.com/jeffh/sniffer/',
    requires=[
        'python-termstyle',
        'nose',
    ],
    entry_points = {
        'console_scripts': ['sniffer = sniffer:main'],
    },
    packages=find_packages(),
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
    ],
)
