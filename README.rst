Overview
========

``sniffer`` is a autotest tool for Python_ using the nosetest_ library.

**NEW**: sniffer can now be customize to run anything, see 'Advanced Usage'.

Sniffer will automatically re-run tests if your code changes. And with another third-party
library (see below), the CPU usage of file system monitoring is reduced in comparison
to pure-python solutions. However, sniffer will still work without any of those libraries.

.. _Python: http://python.org/
.. _nosetest: http://code.google.com/p/python-nose/

Looking for maintainers
-----------------------

I (@jeffh) am looking for a new maintainer to carry on this project to new heights. I'm currently leaving this project on maintance mode (respond to issues, merge pull requests), but I'm not dedicating most of my free time towards this project.

Contact me on twitter (@jeffhui) or via email if you're interested in taking over the helm of this project.

Usage
-----

To install::

  pip install sniffer

Simply run ``sniffer`` in your project directory.

You can use ``sniffer --help`` for options And like autonose_, you can pass the nose
arguments with *-x* prefix: ``-x--with-doctest`` or ``-x--config``.

The problem with autonose_, is that the autodetect can be slow to detect changes. This is due
to the pure python implementation - manually walking through the file system to see what's
changed [#]_. Although the default install of sniffer shares the same problem, installing a
third-party library can help fix the problem. The library is dependent on your operating system:

- If you use **Linux**, you'll need to install pyinotify_.
- If you use **Windows**, you'll need to install pywin32_.
- If you use **Mac OS X** 10.5+ (Leopard), you'll need to install MacFSEvents_.

If you want support for other notification systems, you can install:

- gntp_ for Growl_ support (Mac OS X).
- osxnotify_ and libosxnotify_ for native OS X notifications (Max OS X 10.9.4 and newer)
- py-notify_ for LibNotify_ support (Linux).

.. [#] This has been resolved in subsequent autonose versions, using watchdog.
.. _nose: http://code.google.com/p/python-nose/
.. _easy_install: http://pypi.python.org/pypi/setuptools
.. _pip: http://pypi.python.org/pypi/pip
.. _autonose: http://github.com/gfxmonk/autonose
.. _pyinotify: http://trac.dbzteam.org/pyinotify
.. _pywin32: http://sourceforge.net/projects/pywin32/
.. _MacFSEvents: http://pypi.python.org/pypi/MacFSEvents/0.2.1
.. _gntp: https://github.com/kfdm/gntp/
.. _Growl: http://growl.info
.. _py-notify: http://home.gna.org/py-notify
.. _LibNotify: http://developer-next.gnome.org/libnotify/
.. _osxnotify: https://github.com/tomekwojcik/osxnotify-python
.. _libosxnotify: https://github.com/tomekwojcik/libosxnotify

Advanced Usage
--------------

Don't want to run nose? You can do whatever you really want. Create a scent.py file in
your current working directory. Here's an example of what you can do so far:

.. code-block:: python

  from sniffer.api import * # import the really small API
  import os, termstyle

  # you can customize the pass/fail colors like this
  pass_fg_color = termstyle.green
  pass_bg_color = termstyle.bg_default
  fail_fg_color = termstyle.red
  fail_bg_color = termstyle.bg_default

  # All lists in this variable will be under surveillance for changes.
  watch_paths = ['.', 'tests/']

  # this gets invoked on every file that gets changed in the directory. Return
  # True to invoke any runnable functions, False otherwise.
  #
  # This fires runnables only if files ending with .py extension and not prefixed
  # with a period.
  @file_validator
  def py_files(filename):
      return filename.endswith('.py') and not os.path.basename(filename).startswith('.')

  # This gets invoked for verification. This is ideal for running tests of some sort.
  # For anything you want to get constantly reloaded, do an import in the function.
  #
  # sys.argv[0] and any arguments passed via -x prefix will be sent to this function as
  # it's arguments. The function should return logically True if the validation passed
  # and logicially False if it fails.
  #
  # This example simply runs nose.
  @runnable
  def execute_nose(*args):
      import nose
      return nose.run(argv=list(args))

And that's the basic case. Nothing too fancy shmanshe. You can have multiple file_validator and
runnable decorators if you want.

There is also support for selecting a runnable function by file validator.
Useful if you want to run nose for Python files, mocha for JavaScript files,
and csslint for CSS. Or any other combination you can come up with. For
example:

.. code-block:: python

    # Here we instruct the 'python_tests' runnable to be kicked off
    # when a .py file is changed
    @select_runnable('python_tests')
    @file_validator
    def py_files(filename):
        return filename.endswith('.py') and not os.path.basename(filename).startswith('.')


    # Here we instruct the 'javascript_tests' runnable to be kicked off
    # when a .js file is changed
    @select_runnable('javascript_tests')
    @file_validator
    def js_files(filename):
        return filename.endswith('.js') and not os.path.basename(filename).startswith('.')


    @runnable
    def python_tests(*args):
        import nose
        return nose.run(argv=list(args))


    @runnable
    def javascript_tests(*args):
        command = "mocha tests/js-tests.js"
        return call(command, shell=True) == 0

This will run the nose for modifications to Python files and mocha when
JavaScript files are changed.


Other Uses
==========

Running with Other Test Frameworks
----------------------------------

If you want to run another unit testing framework, you can do so by overriding ``sniffer.Sniffer``,
which is the class that handles running tests, or whatever you want. Specifically, you'll want to
override the ``run``, method to configure what you need to be done.

The property, ``test_args``, are arguments gathered through ``--config=blah`` and ``-x.*``
configuration options. You should perform you imports inside the function instead of outside,
to let the class reload the test framework (and reduce possibilities of multiple-run bugs).

After subclassing, set sniffer_instance parameter to your custom class when calling run
or main.

Current Issues
==============

For linux, there is an exception that is sometimes thrown when terminating.

Currently the program only looks for changes in the current working directory. This isn't the
best solution: it doesn't understand how changes to your source code affects it.
