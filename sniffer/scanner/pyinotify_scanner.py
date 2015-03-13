"""
Scanner that relies on the pyinotify (Unix) Library

It eliminates constant watching mechanisms
"""
from __future__ import absolute_import
from .base import BaseScanner

import pyinotify


class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, scanner):
        self._scanner = scanner

    def process_IN_CREATE(self, event):
        if self._scanner.is_valid_type(event.pathname):
            self._scanner.trigger_created(event.pathname)

    def process_IN_DELETE(self, event):
        if self._scanner.is_valid_type(event.pathname):
            self._scanner.trigger_deleted(event.pathname)

    def process_IN_MODIFY(self, event):
        #self._process('modified', event.pathname)
        if self._scanner.is_valid_type(event.pathname):
            self._scanner.trigger_modified(event.pathname)

    def process_IN_MOVED_FROM(self, event):
        if self._scanner.is_valid_type(event.pathname):
            self._scanner.trigger_deleted(event.pathname)

    def process_IN_MOVED_TO(self, event):
        print('got moved to')
        #self._process('modified', event.pathname)
        if self._scanner.is_valid_type(event.pathname):
            self._scanner.trigger_modified(event.pathname)


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
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE | pyinotify.IN_MODIFY | \
            pyinotify.IN_MOVED_TO | pyinotify.IN_MOVED_TO
        for path in self.paths:
            self._watcher.add_watch(path, mask, rec=True, auto_add=True,
                                    exclude_filter=self.is_valid_type)

        return notifier

    def loop(self, sleep_time=None, callback=None):
        self.trigger_init()
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
