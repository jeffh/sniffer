"""
Scanner class.

Provides a polling technique which is an OS-independent and uses no third-party
libraries at the cost of performance. The polling technique constantly walks through
the directory tree to see which files changed, calling os.stat on the files.

Using Scanner.inject, custom third-party mixin classes can be used.
"""
import os
import time

class BaseScanner(object):
    """
    Provides basic hooking and logging mechanisms.
    """
    ALL_EVENTS = ('created', 'modified', 'deleted', 'init')
    def __init__(self, path, file_validator=None, logger=None):
        self._validator = file_validator
        self._path = os.path.abspath(path)
        self._logger = logger
        self._events = {}
        for e in self.ALL_EVENTS:
            self._events[e] = []

    @property
    def path(self):
        """
        The directory to watch.
        """
        return self._path

    def log(self, *message):
        """
        Logs a messate to a defined io stream if available.
        """
        if self._logger is None:
            return
        s = " ".join([str(m) for m in message])
        self._logger.write(s+'\n')
        self._logger.flush()

    def trigger(self, event_name, *args, **kwargs):
        """
        Triggers a given event with the following *args and **kwargs parameters.
        """
        self.log('event: %s' % event_name, *args)
        for f in self._events[event_name]:
            f(*args, **kwargs)

    def is_valid_type(self, filepath):
        """
        Returns True if the given filepath is a valid watchable filetype.
        The filepath can be assumed to be a file (not a directory).
        """
        if self._validator is not None:
            return self._validator(filepath, self.path)
        if filepath.endswith('.py') and not os.path.basename(filepath).startswith('.'):
            return True
        return False

    def _modify_event(self, event_name, method, func):
        """
        Wrapper to call a list's method from one of the events
        """
        if event_name not in self.ALL_EVENTS:
            raise TypeError('event_name can only be one of the following: %s' % \
                            repr(self.ALL_EVENTS))
        if not callable(func):
            raise TypeError('func must be callable to be added as an observer.')
        getattr(self._events[event_name], method)(func)

    def observe(self, event_name, func):
        """
        event_name := {'added', 'modified', 'removed'}, list, tuple
        
        Attaches a function to run to a particular event. The function must be
        unique to be removed cleanly. Alternatively, event_name can be an list/tuple
        if any of the string possibilities to be added on multiple events.
        """
        if isinstance(event_name, list) or isinstance(event_name, tuple):
            for name in event_name:
                self.observe(name, func)
            return
        self.log(func.__name__, "attached to", event_name)
        self._modify_event(event_name, 'append', func)

    def unobserve(self, event_name, func):
        """
        event_name := {'added', 'modified', 'removed'}, list, tuple
        
        Removes an observer function from a particular event that was added by
        observe().
        """
        if isinstance(event_name, list) or isinstance(event_name, tuple):
            for name in event_name:
                self.unobserve(name, func)
            return
        self.log(func.__name__, "dettached from", event_name)
        self._modify_event(event_name, 'remove', func)

class PollingScanner(BaseScanner):
    """
    Implements the naive, but cross-platform file scanner.
    """
    def __init__(self, *args, **kwargs):
        super(PollingScanner, self).__init__(*args, **kwargs)
        self._watched_files = {}

    def get_modified_time(self, filepath):
        """Returns the modified type for the given filepath or None on failure"""
        if not os.path.isfile(filepath):
            return None
        return os.stat(filepath).st_mtime

    def watch_file(self, filepath, trigger_event=True):
        """Adds the file's modified time into its internal watchlist."""
        try:
            is_new = filepath not in self._watched_files
            self._watched_files[filepath] = self.get_modified_time(filepath)
        except OSError:
            return # didn't happen
        if trigger_event:
            if is_new:
                self.trigger('created', filepath)
            else:
                self.trigger('modified', filepath)

    def unwatch_file(self, filepath, trigger_event=True):
        """
        Removes the file from the internal watchlist if exists.
        """
        if filepath not in self._watched_files:
            return
        if trigger_event:
            self.trigger('deleted', filepath)
        del self._watched_files[filepath]

    def is_modified(self, filepath):
        """
        Returns True if the file has been modified since last seen.
        Will return False if the file has not been seen before.
        """
        if self.is_new(filepath):
            return False
        mtime = self.get_modified_time(filepath)
        return self._watched_files[filepath] < mtime

    def requires_new_modtime(self, filepath):
        """Returns True if the stored modtime needs to be updated."""
        return self.is_new(filepath) or self.is_modified(filepath)
    
    def is_new(self, filepath):
        """Returns True if file is not already on the watch list."""
        return filepath not in self._watched_files

    def loop(self, sleep_time=1):
        """
        Goes into a blocking IO loop. If polling is used, the sleep_time is
        the interval, in seconds, between polls.
        """
        self.log("""
No supported libraries found: using polling-method.

You may want to install a third-party library for performance benefits.
Supported libraries are:
  - pyinotify (Linux)
  - pywin32 (Windows)
  - MacFSEvents (OSX Leopard)
""")
        self._scan(trigger=False)
        self.trigger('init')
        while 1:
            self._scan()
            time.sleep(sleep_time)

    def _scan(self, trigger=True):
        """
        Walks through the directory to look for changes of the given file types.
        Returns True if changes occurred (False otherwise).
        Returns None if polling method isn't being used.
        """
        changed = False
        files_seen = []
        os_path_join = os.path.join
        for root, dirs, files in os.walk(self._path):
            for f in files:
                fpath = os_path_join(root, f)
                if not self.is_valid_type(fpath):
                    continue
                files_seen.append(fpath)
                if self.requires_new_modtime(fpath):
                    self.watch_file(fpath, trigger)
                    changed = True
        files_seen = set(files_seen)
        for f in self._watched_files.keys():
            if f not in files_seen:
                self.unwatch_file(f, trigger)
                changed = True
        return changed
