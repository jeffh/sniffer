"""
Sniffer - An automatic test runner for Nose
==========

This is a simple program that runs nose anytime the current working
directory (or its subdirectories) have changed (added, modified, or
delete files).

*Note:* By default, sniffer polls the directory tree to determine what changed.
This method was used because of its:

 - simplicity: It's pretty easy to write.
 - cross-platform: Unlike third-party libs, which only work on one OS.
 - standard: Uses only standard modules.

Alternatively, third party modules can be installed to increase performance.
The library to install is dependent on your operating system:

 - Linux: install pyinotify
 - Windows: install pywin32
 - OSX: install MacFSEvents

"""

from .metadata import *
from .scanner import Scanner
from .runner import Sniffer
from .main import main, run

__all__ = ['Scanner', 'Sniffer', 'main', 'run']
