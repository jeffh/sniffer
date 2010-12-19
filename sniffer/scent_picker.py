g = globals().copy()
import os, sys, termstyle

class ScentModule(object):
    def __init__(self, mod, filename):
        self.mod = mod
        self.filename = filename
        self.validators = []
        self.runners = []
        for name in dir(self.mod):
            obj = getattr(self.mod, name)
            type = getattr(obj, 'scent_api_type', None)
            if type == 'runnable':
                self.runners.append(obj)
            elif type == 'file_validator':
                self.validators.append(obj)
        self.runners = tuple(self.runners)
        self.validators = tuple(self.validators)
        print self.validators
        
    def reload(self):
        return load_file(self.filename)
    
    def run(self, args):
        for r in self.runners:
            if not r(*args):
                return False
        return True
        
    @property
    def fg_pass(self):
        return getattr(self.mod, 'pass_fg_color', termstyle.white)
    @property
    def bg_pass(self):
        return getattr(self.mod, 'pass_bg_color', termstyle.bg_green)
    
    @property
    def fg_fail(self):
        return getattr(self.mod, 'fail_fg_color', termstyle.white)
    @property
    def bg_fail(self):
        return getattr(self.mod, 'fail_bg_color', termstyle.bg_red)

def load_file(filename):
    "Runs the given scent.py file."
    mod_name = '.'.join(os.path.basename(filename).split('.')[:-1])
    mod_path = os.path.dirname(filename)
    
    global_vars = globals()
    if mod_name in sys.modules.keys():
        del sys.modules[mod_name]
    if mod_path not in set(sys.modules.keys()):
        sys.path.insert(0, mod_path)
    return ScentModule(__import__(mod_name, g, g), filename)
    
def exec_from_dir(dirname=None, scent="scent.py"):
    """Runs the scent.py file from the given directory (cwd if None given).
    
    Returns module if loaded a scent, None otherwise.
    """
    if dirname is None:
        dirname = os.getcwd()
    files = os.listdir(dirname)
    
    if scent not in files:
        return None
    
    return load_file(os.path.join(dirname, scent))
