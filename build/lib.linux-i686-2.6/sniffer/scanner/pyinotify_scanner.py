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
        self._watcher = pyinotify.WatchManager()
        self._notifier = self._generate_notifier()

    def __deinit__(self):
        if self._notifier is not None:
            self._notifier.stop()

    def _generate_notifier(self):
        handler = EventHandler(self)

        notifier = pyinotify.Notifier(self._watcher, handler)
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY
        for path in self.paths:
            self._watcher.add_watch(path, mask, rec=True)
        
        return notifier

    def loop(self, sleep_time=None, callback=None):
        self.trigger('init')
        try:
            self._notifier.loop(callback)
        except KeyboardInterrupt:
            self._notifier.stop()
            raise

    def step(self):
        self._notifier.process_events()
        if self._notifier.check_events(timeout=1000):
            self.read_events()
        self._notifier.stop()

    def stop(self):
        self._notifier.stop()
