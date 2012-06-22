"""
File watching on windows using the Win32API.
Requires the pywin32 library

The code is based off Tim Golden's work:
http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
"""
from base import BaseScanner
import win32file
import win32con
import os

ACTIONS = {}
for i, name in enumerate(('Created', 'Deleted', 'Updated', 'Renamed from', 'Renamed to')):
    ACTIONS[i] = name
FILE_LIST_DIR = 0x0001

class PyWinScanner(BaseScanner):
    """
    Scanner built on PyWin32 (aka, Win32API).
    """
    def __init__(self, *args, **kwargs):
        super(PyWinScanner, self).__init__(*args, **kwargs)
        self._running = False
        
    def _get_handle(self, path):
        return win32file.CreateFile(
            path,                                                 # filename
            FILE_LIST_DIR,                                        # desired access
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE, # share mode
            None,                                                 # security attrs
            win32con.OPEN_EXISTING,                               # creation disposition
            win32con.FILE_FLAG_BACKUP_SEMANTICS,                  # flags & attrs
            None                                                  # template file (?)
        )

    def _get_changes(self, handle):
        return win32file.ReadDirectoryChangesW(
            handle, # directory handle
            1024, # buffer len (return size)
            True, # watch recursively
            # notify filters
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME | # create/rename/delete files
            #win32con.FILE_NOTIFY_CHANGE_DIR_NAME | # create/rename/delete dirs
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE, #| # on system write
            #win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
            #win32con.FILE_NOTIFY_CHANGE_SIZE |
            #win32con.FILE_NOTIFY_CHANGE_SECURITY,
            None, # overlapped structure (?)
            None  # completion routine (async only)
        )

    def step(self):
        for path, handle in ((p, self._get_handle(p)) for p in self.paths):
            results = self._get_changes(handle)
            for action, filename in results:
                fullpath = os.path.join(path, filename)
                if self.is_valid_type(fullpath):
                    continue
                action = ACTIONS.get(action, "unknown")
                if action == 'Created':
                    self.trigger_created(fullpath)
                elif action in ('Updated', 'Renamed to'):
                    self.trigger_modified(fullpath)
                elif action == 'Deleted':
                    self.trigger_deleted(fullpath)
        
    def loop(self, sleep_time=None):
        self.log("Library of choice: PyWin32 (eww)")
        self.trigger_init()
        self._running = True
        while self._running:
            self.step()
            # TODO: figure out if we really need to sleep

    def stop(self):
        self._running = False
