"""
Scanner that relies on the FSEvents (OSX) library.

This is done through MacFSEvents
"""
import os
import fsevents
import time

class FSEventsScanner(object):
    """
    This works with MacFSEvents to hook into OSX's file watching mechanisms.
    """
    def _generate_observer(self):
        observer = fsevents.Observer()
        # use file_events=True to mimic other implementations
        for path in self.paths:
            stream = fsevents.Stream(self._callback, path, file_events=True)
            observer.schedule(stream)
        return observer
        
    def loop(self, sleep_time=None):
        self.log("Library of choice: MacFSEvents")
        self._trigger('init')
        observer = self._generate_observer()
        # observer.start() # separate thread
        observer.run() # blocking

    def stop(self):
        observer.stop()

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
            self.trigger('modified', event.name)
        if event.mask & fsevents.IN_CREATE:
            self.trigger('created', event.name)
        if event.mask & fsevents.IN_DELETE:
            self.trigger('deleted', event.name)
