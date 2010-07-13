from base import BaseScanner
import platform

import pyinotify

class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, scanner):
        self._scanner = scanner

    def _process(self, event_type, filepath):
        if self._scanner.is_valid_type(filepath):
            self._scanner.trigger(event_type, filepath)

    def process_IN_CREATE(self, event):
        self._process('created', event.pathname)

    def process_IN_DELETE(self, event):
        self._process('deleted', event.pathname)

    def process_IN_MODIFY(self, event):
        self._process('modified', event.pathname)

class PyINotifyScanner(BaseScanner):
    """
    Scanner that uses pyinotify (alias, inotify) for notification events.
    """
    def __init__(self, *args, **kwargs):
        super(PyINotifyScanner, self).__init__(*args, **kwargs)
        self.log("Library of choice: pyinotify")

    def loop(self, sleep_time=None):
        self.trigger('init')
        watcher = pyinotify.WatchManager()
        handler = EventHandler(self)
        
        notifier = pyinotify.Notifier(watcher, handler)
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY
        watcher.add_watch(self.path, mask, rec=True)
        
        notifier.loop()
