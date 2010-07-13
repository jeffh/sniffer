from optparse import OptionParser
from scanner import Scanner
from helpers import ColoredOutput, ModulesRestorePoint
import os
import sys
import platform

__all__ = ['run_nose', 'clear_on_run', 'run', 'main']

# for debugging
def echo(text):
    def wrapped(filepath):
        print text % {'file': filepath}
    return wrapped


def run_nose(config=None, args=()):
    """
    Runs the nose tests.
    """
    # import here to prevent annoying:
    #  "TypeError: 'NoneType' object is not callable"
    # when printing something in your program you're testing.
    # 
    # moving the import here reforces it to be reloaded by ModulesRestorePoint
    #
    # error documented here: http://github.com/gfxmonk/autonose/issues#issue/13
    import nose
    arguments = [sys.argv[0]] + list(args)
    if config is not None:
        arguments.append('--config=%s' % config)
    try:
        if nose.run(argv=arguments):
            ColoredOutput.instance().writeln("In good standing",
                                             color=ColoredOutput.BRIGHT_GREEN)
        else:
            ColoredOutput.instance().writeln("Failed - Back to work!",
                                             color=ColoredOutput.BRIGHT_RED)
    except StandardError:
        import traceback
        traceback.print_exc()
        sys.exit(1)

def clear_on_run(*args):
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')
    print "Nose Tests:"

def run(wait_time=0.5, color=True, clear=True, nose_config=None, nose_argsv=(), debug=False):
    """
    Runs the auto tester loop.
    """
    ColoredOutput.instance().use_color = color
    modules = ModulesRestorePoint()
    if debug:
        scanner = Scanner('.', logger=sys.stdout)
    else:
        scanner = Scanner('.')
    # order matters here!
    def restore_modules(*args):
        modules.restore()
    scanner.observe(scanner.ALL_EVENTS, restore_modules)
    if clear:
        scanner.observe(scanner.ALL_EVENTS, clear_on_run)
    def run_nosetests(*args):
        run_nose(nose_config, nose_argsv)
    scanner.observe(scanner.ALL_EVENTS, run_nosetests)
    #scanner.observe('added',    echo("added   %(file)s"))
    #scanner.observe('modified', echo("changed %(file)s"))
    #scanner.observe('removed',  echo("delete  %(file)s"))
    scanner.loop(wait_time)

def main(progname):
    parser = OptionParser()
    parser.add_option('-w', '--wait', dest="wait_time", metavar="TIME",
                      help="Wait time, in seconds, before possibly rerunning tests. "
                      "(default: %default)",
                      default=0.5, type="float")
    parser.add_option('--no-color', dest="use_color", default=True, action="store_false",
                      help="Disable use of color in the terminal.")
    parser.add_option('--no-clear', dest="clear_on_run", default=True, action="store_false",
                      help="Disable the clearing of screen")
    parser.add_option('--debug', dest="debug", default=False, action="store_true",
                      help="Enabled debugging output. (default: %default)")
    parser.add_option('-c', '--config', dest="nose_config", metavar="FILE", default=None,
                      help="Optional configuration file to pass to nose.")
    parser.add_option('-x', '--nose-arg', dest="nose_args", default=[], action="append",
                      help="Optional arguments to pass to nose (use multiple times to pass "
                      "multiple arguments.)")
    (options, args) = parser.parse_args()
    if options.debug:
        print "Options:", options
    try:
        print "Starting watch..."
        run(options.wait_time, options.use_color, options.clear_on_run,
            options.nose_config, options.nose_args, options.debug)
    except KeyboardInterrupt:
        print "Good bye."
    except Exception:
        import traceback
        traceback.print_exc()
        print "Burning down."
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[0]))
