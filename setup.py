from setuptools import setup, find_packages

# will fail to install via pip/easy_install
#from sniffer.metadata import __version__, __author__, __author_email__

__version__, __author__, __author_email__ = "0.2.4", "Jeff Hui", "contrib@jeffhui.net"

requires=[
    'python-termstyle',
    'nose',
]

# Require colorama on Windows to support terminal color.
if os.name == 'nt':
    requires.append("colorama")

setup(
    name='sniffer',
    version=__version__,
    description='An automatic test runner. Supports nose out of the box.',
    long_description=open('README.rst').read(),
    author=__author__,
    author_email=__author_email__,
    url='http://github.com/jeffh/sniffer/',
    install_requires=requires,
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
