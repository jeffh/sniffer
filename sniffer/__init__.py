"""
Sniffer - An automatic test runner for Nose
==========

This is a simple program that runs nose anytime the current working
directory (or its subdirectories) have changed (added, modified, or
delete files).

*Note:* This does not use any third-party libraries, other than nose,
so a regular poll of the directory tree is used to determine what
changed. This method was used because of its:

 - simplicity: It's pretty easy to write.
 - cross-platform: Unlike third-party libs, which only work on one OS.
 - standard: Uses only standard modules.

Alternatively, third party modules can be installed to increase performance.
The library to install is dependent on your operating system:

 - Linux: install pyinotify
 - Windows: install pywin32
 - OSX: install MacFSEvents

"""
__author__ = "Jeff Hui"
__author_email__ = 'contrib@jeffhui.net'
__copyright__ = "Copyright 2010, Jeff Hui"
__credits__ = ["Jeff Hui"]

__license__ = "MIT"
__version__ = "0.8"

from scanner import Scanner
from main import main, run
import sys

__all__ = ['main', 'run', 'Scanner']

if __name__ == '__main__':
    sys.exit(main(sys.argv[0]))
