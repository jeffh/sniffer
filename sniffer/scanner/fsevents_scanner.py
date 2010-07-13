"""
Scanner that relies on the FSEvents (OSX) library.

This is done through MacFSEvents
"""
import os
import fsevents

class FSEventsScanner(object):
    """
    This works with MacFSEvents to hook into OSX's file watching mechanisms.
    """
    def loop(self, sleep_time=None):
        self.log("Library of choice: MacFSEvents")
        self._trigger('init')
        observer = fsevents.Observer()
        # use file_events=True to mimic other implementations
        stream = fsevents.Stream(self._callback, self.path, file_events=True)
        observer.schedule(stream)
        # observer.start() # separate thread
        observer.run() # blocking

    def _callback(self, event):
        if event.mask & (fsevents.IN_MODIFY):
            self.trigger('modified', event.name)
        if event.mask & fsevents.IN_CREATE:
            self.trigger('created', event.name)
        if event.mask & fsevents.IN_DELETE:
            self.trigger('deleted', event.name)
