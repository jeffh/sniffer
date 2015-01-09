"""
Main runners. Bootloads Sniffer class.
"""
from __future__ import print_function, absolute_import
from optparse import OptionParser
from sniffer.scanner import Scanner
from sniffer.runner import ScentSniffer
from sniffer.metadata import __version__
import sys

import colorama
colorama.init()

__all__ = ['run', 'main']


def run(sniffer_instance=None, wait_time=0.5, clear=True, args=(),
        debug=False):
    """
    Runs the auto tester loop. Internally, the runner instanciates the sniffer_cls and
    scanner class.

    ``sniffer_instance`` The class to run. Usually this is set to but a subclass of scanner.
                    Defaults to Sniffer. Sniffer class documentation for more information.
    ``wait_time``   The time, in seconds, to wait between polls. This is dependent on
                    the underlying scanner implementation. OS-specific libraries may choose
                    to ignore this parameter. Defaults to 0.5 seconds.
    ``clear``       Boolean. Set to True to clear the terminal before running the sniffer,
                    (alias, the unit tests). Defaults to True.
    ``args``        The arguments to pass to the sniffer/test runner. Defaults to ().
    ``debug``       Boolean. Sets the scanner and sniffer in debug mode, printing more internal
                    information. Defaults to False (and should usually be False).
    """
    if sniffer_instance is None:
        sniffer_instance = ScentSniffer()

    if debug:
        scanner = Scanner(
            sniffer_instance.watch_paths,
            scent=sniffer_instance.scent, logger=sys.stdout)
    else:
        scanner = Scanner(
            sniffer_instance.watch_paths, scent=sniffer_instance.scent)
    #sniffer = sniffer_cls(tuple(args), clear, debug)
    sniffer_instance.set_up(tuple(args), clear, debug)

    sniffer_instance.observe_scanner(scanner)
    scanner.loop(wait_time)

def main(sniffer_instance=None, test_args=(), progname=sys.argv[0],
         args=sys.argv[1:]):
    """
    Runs the program. This is used when you want to run this program standalone.

    ``sniffer_instance`` A class (usually subclassed of Sniffer) that hooks into the
                    scanner and handles running the test framework. Defaults to
                    Sniffer instance.
    ``test_args``   This function normally extracts args from ``--test-arg ARG`` command. A
                    preset argument list can be passed. Defaults to an empty tuple.
    ``program``     Program name. Defaults to sys.argv[0].
    ``args``        Command line arguments. Defaults to sys.argv[1:]
    """
    parser = OptionParser(version="%prog " + __version__)
    parser.add_option('-w', '--wait', dest="wait_time", metavar="TIME",
                      default=0.5, type="float",
                      help="Wait time, in seconds, before possibly rerunning"
                      "tests. (default: %default)")
    parser.add_option('--no-clear', dest="clear_on_run", default=True,
                      action="store_false",
                      help="Disable the clearing of screen")
    parser.add_option('--debug', dest="debug", default=False,
                      action="store_true",
                      help="Enabled debugging output. (default: %default)")
    parser.add_option('-x', '--test-arg', dest="test_args", default=[],
                      action="append",
                      help="Arguments to pass to nose (use multiple times to "
                      "pass multiple arguments.)")
    (options, args) = parser.parse_args(args)
    test_args = test_args + tuple(options.test_args)

    if options.debug:
        print("Options:", options)
        print("Test Args:", test_args)
    try:
        print("Starting watch...")
        run(sniffer_instance, options.wait_time, options.clear_on_run,
            test_args, options.debug)
    except KeyboardInterrupt:
        print("Good bye.")
    except Exception:
        import traceback
        traceback.print_exc()
        return sys.exit(1)
    return sys.exit(0)

if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    main()
