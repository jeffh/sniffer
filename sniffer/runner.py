from modules_restore_point import ModulesRestorePoint
from functools import wraps
from termstyle import bg_red, bg_green, white
import platform
import os
import sys
import scent_picker

__all__ = ['Sniffer']

# for debugging
def echo(text):
    def wrapped(filepath):
        print text % {'file': filepath}
    return wrapped

class Sniffer(object):
    """
    Handles the execution of the sniffer. The interface that main.run expects is:

    ``set_up(test_args, clear, debug)``
    
      ``test_args`` The arguments to pass to the test runner.
      ``clear``     Boolean. Set to True if we should clear console before running
                    the tests.
      ``debug``     Boolean. Set to True if we want to print debugging information.

    ``observe_scanner(scanner)``

      ``scanner``   The scanner instance to hook events into. By default, ``self._run`` is
                    attached, which then calls self.run(). The run method should return
                    True on passing and False on failure.
    """
    def __init__(self):
        self.modules = ModulesRestorePoint()
        self._scanners = []
        self.pass_colors = {'fg': white, 'bg': bg_green}
        self.fail_colors = {'fg': white, 'bg': bg_red}
        self.set_up()
        
    def set_up(self, test_args=(), clear=True, debug=False):
        """
        Sets properties right before calling run.

          ``test_args`` The arguments to pass to the test runner.
          ``clear``     Boolean. Set to True if we should clear console before running
                        the tests.
          ``debug``     Boolean. Set to True if we want to print debugging information.
        """
        self.test_args = test_args
        self.debug, self.clear = debug, clear
        
    def absorb_args(self, func):
        """
        Calls a function without any arguments. The returned caller function
        accepts any arguments (and throws them away).
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func()
        return wrapper
    
    def observe_scanner(self, scanner):
        """
        Hooks into multiple events of a scanner.
        """
        scanner.observe(scanner.ALL_EVENTS, self.absorb_args(self.modules.restore))
        if self.clear:
            scanner.observe(scanner.ALL_EVENTS, self.absorb_args(self.clear_on_run))
        scanner.observe(scanner.ALL_EVENTS, self.absorb_args(self._run))
        if self.debug:
            scanner.observe('created',  echo("callback - created  %(file)s"))
            scanner.observe('modified', echo("callback - changed  %(file)s"))
            scanner.observe('deleted',  echo("callback - deleted  %(file)s"))
        self._scanners.append(scanner)

    def clear_on_run(self):
        """Clears console before running the tests."""
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')
        print "Running Tests:"

    def _stop(self):
        """Calls stop() to all scanner in an attempt to quit."""
        for scanner in self._scanners:
            scanner.stop()

    def _run(self):
        """Calls self.run() and wraps for errors."""
        try:
            if self.run():
                print self.pass_colors['bg'](self.pass_colors['fg']("In good standing"))
            else:
                print self.fail_colors['bg'](self.fail_colors['fg']("Failed - Back to work!"))
        except StandardError:
            import traceback
            traceback.print_exc()
            self._stop()
            raise
        except Exception:
            self._stop()
            raise
        return True

    def run(self):
        """
        Runs the unit test framework. Can be overridden to run anything.
        Returns True on passing and False on failure.
        """
        # import here instead of on top:
        # - To force a module reload to resolve this bug until Nose fixes it:
        #   http://github.com/gfxmonk/autonose/issues#issue/13
        try:
            import nose
            arguments = [sys.argv[0]] + list(self.test_args)
            return nose.run(argv=arguments)
        except ImportError:
            print
            print "*** Nose library missing. Please install it. ***"
            print
            raise

class ScentSniffer(Sniffer):
    """Runs arbitrary python code in the cwd's scent.py file."""
    def __init__(self, cwd=None, scent="scent.py"):
        self.cwd = cwd or os.getcwd()
        self.scent = scent_picker.exec_from_dir(self.cwd, scent)
        super(ScentSniffer, self).__init__()
        self.update_from_scent()
        
    def update_from_scent(self):
        if self.scent:
            self.pass_colors['fg'] = self.scent.fg_pass
            self.pass_colors['bg'] = self.scent.bg_pass
            self.fail_colors['fg'] = self.scent.fg_fail
            self.fail_colors['bg'] = self.scent.bg_fail
        
    def refresh_scent(self, filepath):
        if self.scent and filepath == self.scent.filename:
            print "Reloaded Scent:", filepath
            for s in self._scanners:
                self.unobserve_scanner(s)
            self.scent = self.scent.reload()
            self.update_from_scent()
            
    def unobserver_scanner(self, scanner):
        for v in self.scent.validators:
            scanner.remove_validator(v)
    
    def observe_scanner(self, scanner):
        if self.scent:
            for v in self.scent.validators:
                scanner.add_validator(v)
        scanner.observe('created', self.refresh_scent)    
        scanner.observe('modified', self.refresh_scent)
        return super(ScentSniffer, self).observe_scanner(scanner)
        
    def run(self):
        """
        Runs the CWD's scent file.
        """
        if not self.scent or len(self.scent.runners) == 0:
            print "Could not find 'scent.py', running nose."
            return super(ScentSniffer, self).run()
        else:    
            arguments = [sys.argv[0]] + list(self.test_args)
            return self.scent.run(arguments)
        return True
