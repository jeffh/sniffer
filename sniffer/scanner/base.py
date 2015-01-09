"""
Scanner class.

Provides a polling technique which is an OS-independent and uses no third-party
libraries at the cost of performance. The polling technique constantly walks
throughthe directory tree to see which files changed, calling os.stat on the
files.
"""
import os
import time
import collections


class BaseScanner(object):
    """
    Provides basic hooking and logging mechanisms.
    """
    ALL_EVENTS = ('created', 'modified', 'deleted', 'init')

    def __init__(self, paths, scent=None, logger=None, *args, **kwargs):
        self._validators = []
        self._scent = scent
        self._paths = [os.path.abspath(p) for p in paths]
        self._logger = logger
        self._events = {}
        for e in self.ALL_EVENTS:
            self._events[e] = []
        self._watched_files = {}

    def add_validator(self, func):
        if not isinstance(func, collections.Callable):
            raise TypeError(("Param should return boolean and accept a "
                             "filename string"))
        self._validators.append(func)

    def remove_validator(self, func):
        self._validators.remove(func)

    def trigger_modified(self, filepath):
        """Triggers modified event if the given filepath mod time is newer."""
        mod_time = self._get_modified_time(filepath)
        if mod_time > self._watched_files.get(filepath, 0):
            self._trigger('modified', filepath)
            self._watched_files[filepath] = mod_time

    def trigger_created(self, filepath):
        """Triggers created event if file exists."""
        if os.path.exists(filepath):
            self._trigger('created', filepath)

    def trigger_deleted(self, filepath):
        """Triggers deleted event if the flie doesn't exist."""
        if not os.path.exists(filepath):
            self._trigger('deleted', filepath)

    def trigger_init(self):
        """Triggers initialization event."""
        self._trigger('init')

    def _get_modified_time(self, filepath):
        """
        Returns the modified type for the given filepath or None on failure
        """
        if not os.path.isfile(filepath):
            return None
        return os.stat(filepath).st_mtime

    def loop(self, sleep_time=0.5, callback=None):
        """Runs a blocking loop."""
        raise NotImplemented()

    def step(self):
        """
        Looks at changes temporarily before stopping.

        Fires a series of events only once, as defined by the backend. But step
        is always ensured to stop.
        """
        raise NotImplemented()

    def stop(self):
        """
        Used by an event caller to stop the blocking loop.
        """
        raise NotImplemented()

    @property
    def paths(self):
        """
        A tuple of directories to watch.
        """
        return tuple(self._paths)

    def add_path(self, path):
        """
        Adds a directory to watch.
        """
        self._paths.append(path)
        return self

    def log(self, *message):
        """
        Logs a messate to a defined io stream if available.
        """
        if self._logger is None:
            return
        s = " ".join([str(m) for m in message])
        self._logger.write(s+'\n')
        self._logger.flush()

    def _trigger(self, event_name, *args, **kwargs):
        """
        Triggers a given event with the following *args and **kwargs
        parameters.
        """
        self.log('event: %s' % event_name, *args)
        for f in self._events[event_name]:
            f(*args, **kwargs)

    def default_validator(self, filepath):
        """
        The default validator only accepts files ending in .py
        (and not prefixed by a period).
        """
        return filepath.endswith('.py') and \
            not os.path.basename(filepath).startswith('.')

    def in_repo(self, filepath):
        """
        This excludes repository directories because they cause some exceptions
        occationally.
        """
        filepath = set(filepath.replace('\\', '/').split('/'))
        for p in ('.git', '.hg', '.svn', '.cvs', '.bzr'):
            if p in filepath:
                return True
        return False

    def is_valid_type(self, filepath):
        """
        Returns True if the given filepath is a valid watchable filetype.
        The filepath can be assumed to be a file (not a directory).
        """
        if self.in_repo(filepath):
            return False

        validators = self._validators
        if len(validators) == 0:
            validators = [self.default_validator]

        if any([hasattr(v, 'runnable') for v in self._validators]):
            # case where we select the runnable function by the validator
            for validator in validators:
                if validator(filepath):
                    if hasattr(validator, 'runnable'):
                        self._scent.set_runner(validator.runnable)
                        return True
            return False

        for validator in validators:
            if not validator(filepath):
                return False
        return True

    def _modify_event(self, event_name, method, func):
        """
        Wrapper to call a list's method from one of the events
        """
        if event_name not in self.ALL_EVENTS:
            raise TypeError(('event_name ("%s") can only be one of the '
                             'following: %s') % (event_name,
                                                 repr(self.ALL_EVENTS)))
        if not isinstance(func, collections.Callable):
            raise TypeError(('func must be callable to be added as an '
                             'observer.'))
        getattr(self._events[event_name], method)(func)

    def observe(self, event_name, func):
        """
        event_name := {'created', 'modified', 'deleted'}, list, tuple

        Attaches a function to run to a particular event. The function must be
        unique to be removed cleanly. Alternatively, event_name can be an list/
        tuple if any of the string possibilities to be added on multiple events
        """
        if isinstance(event_name, list) or isinstance(event_name, tuple):
            for name in event_name:
                self.observe(name, func)
            return
        self.log(func.__name__, "attached to", event_name)
        self._modify_event(event_name, 'append', func)

    def unobserve(self, event_name, func):
        """
        event_name := {'created', 'modified', 'deleted'}, list, tuple

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
        self._running = False
        self._warn = kwargs.get('warn_missing_lib', True)

    def _watch_file(self, filepath, trigger_event=True):
        """Adds the file's modified time into its internal watchlist."""
        is_new = filepath not in self._watched_files
        if trigger_event:
            if is_new:
                self.trigger_created(filepath)
            else:
                self.trigger_modified(filepath)
        try:
            self._watched_files[filepath] = self._get_modified_time(filepath)
        except OSError:
            return  # didn't happen

    def _unwatch_file(self, filepath, trigger_event=True):
        """
        Removes the file from the internal watchlist if exists.
        """
        if filepath not in self._watched_files:
            return
        if trigger_event:
            self.trigger_deleted(filepath)
        del self._watched_files[filepath]

    def _is_modified(self, filepath):
        """
        Returns True if the file has been modified since last seen.
        Will return False if the file has not been seen before.
        """
        if self._is_new(filepath):
            return False
        mtime = self._get_modified_time(filepath)
        return self._watched_files[filepath] < mtime

    def _requires_new_modtime(self, filepath):
        """Returns True if the stored modtime needs to be updated."""
        return self._is_new(filepath) or self._is_modified(filepath)

    def _is_new(self, filepath):
        """Returns True if file is not already on the watch list."""
        return filepath not in self._watched_files

    def loop(self, sleep_time=1, callback=None):
        """
        Goes into a blocking IO loop. If polling is used, the sleep_time is
        the interval, in seconds, between polls.
        """

        self.log("No supported libraries found: using polling-method.")
        self._running = True
        self.trigger_init()
        self._scan(trigger=False)  # put after the trigger
        if self._warn:
            print("""
You should install a third-party library so I don't eat CPU.
Supported libraries are:
  - pyinotify (Linux)
  - pywin32 (Windows)
  - MacFSEvents (OSX)

Use pip or easy_install and install one of those libraries above.
""")
        while self._running:
            self._scan()
            if isinstance(callback, collections.Callable):
                callback()
            time.sleep(sleep_time)

    def step(self):
        self._scan()

    def stop(self):
        self._running = False

    def _scan(self, trigger=True):
        """
        Walks through the directory to look for changes of the given file
        types.
        Returns True if changes occurred (False otherwise).
        Returns None if polling method isn't being used.
        """
        changed = False
        files_seen = set()
        os_path_join = os.path.join
        for path in self.paths:
            for root, dirs, files in os.walk(path):
                for f in files:
                    fpath = os_path_join(root, f)
                    if not self.is_valid_type(fpath):
                        continue
                    files_seen.add(fpath)
                    if self._requires_new_modtime(fpath):
                        self._watch_file(fpath, trigger)
                        changed = True
            for f in self._watched_files:
                if f not in files_seen:
                    self._unwatch_file(f, trigger)
                    changed = True
        return changed
