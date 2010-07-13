import sys

__all__ = ['ModulesRestorePoint', 'ColoredOutput']

class ModulesRestorePoint(object):
    def __init__(self, sys_modules=sys.modules):
        self._saved_modules = None
        self._sys_modules = sys_modules
        self.save()

    def save(self):
        """Saves the currently loaded modules for restore."""
        self._saved_modules = set(self._sys_modules.keys())

    def restore(self):
        """Unloads all modules that weren't loaded when save_modules was called."""
        sys = set(self._sys_modules.keys())
        for mod_name in sys.difference(self._saved_modules):
            del self._sys_modules[mod_name]

class ColoredOutput(object):
    """Attempts to add colored output to the console."""
    END = '\033[0m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BRIGHT = '\033[1m'
    BRIGHT_RED = BRIGHT+RED
    BRIGHT_GREEN = BRIGHT+GREEN
    BRIGHT_YELLOW = BRIGHT+YELLOW
    BRIGHT_BLUE = BRIGHT+BLUE
    BRIGHT_MAGENTA = BRIGHT+MAGENTA
    BRIGHT_CYAN = BRIGHT+CYAN
    BRIGHT_WHITE = BRIGHT+WHITE
    def __init__(self, stdin=sys.stdout):
        self.io = sys.stdout
        self.use_color = True
    
    @classmethod
    def instance(cls):
        inst = getattr(cls, '_instance', None)
        if not inst:
            cls._instance = inst = cls()
        return inst

    def write(self, *objs, **kwargs):
        s = " ".join(map(str, objs))
        color = kwargs.get('color', None)
        if self.use_color and color:
            self.io.write(color+s+self.END)
        else:
            self.io.write(s)

    def writeln(self, *objs, **kwargs):
        self.write(*objs, **kwargs)
        self.io.write("\n")
        self.io.flush()

    def flush(self):
        self.io.flush()
