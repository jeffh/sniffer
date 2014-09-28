"""
Provides the scanner class which deals with monitoring and notifying changing
in the file system.

It provides a polling technique which is an OS-independent and uses no
third-party libraries at the cost of performance. The polling technique
constantly walks through the directory tree to see which files changed,
calling os.stat on the files.
"""
from __future__ import absolute_import
from .base import PollingScanner

__all__ = ['Scanner']

Scanner = PollingScanner


def _import(module, cls):
    """
    A messy way to import library-specific classes.
    TODO: I should really make a factory class or something, but I'm lazy.
    Plus, factories remind me a lot of java...
    """
    global Scanner

    try:
        cls = str(cls)
        mod = __import__(str(module), globals(), locals(), [cls], 1)
        Scanner = getattr(mod, cls)
    except ImportError:
        pass

_import('pywin_scanner', 'PyWinScanner')          # windows
_import('fsevents_scanner', 'FSEventsScanner')    # osx
_import('pyinotify_scanner', 'PyINotifyScanner')  # linux
