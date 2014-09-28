import sys

__all__ = ['ModulesRestorePoint']


# Really only deletes modules that didn't appear in the restore point.
class ModulesRestorePoint(object):
    def __init__(self, sys_modules=sys.modules):
        self._saved_modules = None
        self._sys_modules = sys_modules
        self.save()

    def save(self):
        """
        Saves the currently loaded modules for restore.
        """
        self._saved_modules = set(self._sys_modules.keys())

    def restore(self):
        """
        Unloads all modules that weren't loaded when save_modules was called.
        """
        sys = set(self._sys_modules.keys())
        for mod_name in sys.difference(self._saved_modules):
            del self._sys_modules[mod_name]
