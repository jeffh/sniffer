"""
Scanner that relies on the MacFSEvents (OSX) library.

This is an OS-specific implementation that eliminates the constant polling of
the directory tree by hooking into OSX's IO events.
"""
from __future__ import absolute_import
from .base import BaseScanner
import fsevents
import time
import sys


class FSEventsScanner(BaseScanner):
    """
    This works with MacFSEvents to hook into OSX's file watching mechanisms.
    """
    def __init__(self, *args, **kwargs):
        super(FSEventsScanner, self).__init__(*args, **kwargs)
        self._observer = self._generate_observer()

    def _generate_observer(self):
        observer = fsevents.Observer()
        # use file_events=True to mimic other implementations
        for path in self.paths:
            stream = fsevents.Stream(self._callback, path, file_events=True)
            observer.schedule(stream)
        return observer

    def loop(self, sleep_time=None):
        self.log("Library of choice: MacFSEvents")
        self.trigger_init()
        # using observer.run() doesn't let us catch the keyboard interrupt
        self._observer.start()  # separate thread
        try:
            while 1:
                time.sleep(60)  # simulate blocking
        except (KeyboardInterrupt, OSError, IOError):
            self.stop()
        #observer.run() # blocking

    def stop(self):
        # Ugly hack, calling Observer.stop() creates a lot of atexit errors
        # that we just want to escape without problems.
        #
        # So we're silently absorbing all the errors
        try:
            from io import StringIO
        except:
            try:
                from cStringIO import StringIO
            except:
                from StringIO import StringIO
        old_err, old_out = sys.stderr, sys.stdout
        sys.stderr, sys.stdout = StringIO(), StringIO()

        self._observer.stop()

        sys.stderr, sys.stdout = old_err, old_out

#    def step(self):
#        observer = self._generate_observer()
#        observer.start()
#        time.sleep(1) # it's really a guess at this point :(
#        observer.stop()
#        observer.join()

    def _callback(self, event):
        if not self.is_valid_type(event.name):
            return
        if event.mask & (fsevents.IN_MODIFY):
            self.trigger_modified(event.name)
        if event.mask & fsevents.IN_CREATE:
            self.trigger_created(event.name)
        if event.mask & fsevents.IN_DELETE:
            self.trigger_deleted(event.name)
