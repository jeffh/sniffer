from modules_restore_point import ModulesRestorePoint
from functools import wraps
from termstyle import bg_red, bg_green
import platform
import os
import sys

__all__ = ['Sniffer']

# for debugging
def echo(text):
    def wrapped(filepath):
        print text % {'file': filepath}
    return wrapped

class Sniffer(object):
    """
    Handles the execution of the sniffer. The interface that main.run expects is:

    ``__init__(test_args, clear, debug)``

      ``test_args`` The arguments to pass to the test runner.
      ``clear``     Boolean. Set to True if we should clear console before running the tests.
      ``debug``     Boolean. Set to True if we want to print debugging information.

    ``observe_scanner(scanner)``

      ``scanner``   The scanner instance to hook events into. By default, ``self._run`` is
                    attached, which then calls self.run(). The run method should return
                    True on passing and False on failure.
    """
    def __init__(self, test_args=(), clear=True, debug=False):
        self.test_args = test_args
        self.modules = ModulesRestorePoint()
        self.debug, self.clear = debug, clear
        self._scanners = []

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
                print bg_green("In good standing")
            else:
                print bg_red("Failed - Back to work!")
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
        # import here instead of on top incase that:
        #  - The module is missing
        #  - Incase nose library is not wanted (ie - another test tool
        #    overrides this method).
        try:
            import nose
            arguments = [sys.argv[0]] + list(self.test_args)
            return nose.run(argv=arguments)
        except ImportError:
            print
            print "*** Nose library missing. Please install it. ***"
            print
            raise

