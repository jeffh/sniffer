Overview
========

``sniffer`` is a autotest tool for Python_ using the nosetest_ library.

**NEW**: sniffer can now be customize to run anything, see 'Advanced Usage'.

Sniffer will automatically re-run tests if your code changes. And with another third-party
library (see below), the CPU usage of file system monitoring is reduced in comparison
to pure-python solutions. However, sniffer will still work without any of those libraries.

.. _Python: http://python.org/
.. _nosetest: http://code.google.com/p/python-nose/

Usage
-----

To install::

  pip install sniffer

Simply run ``sniffer`` in your project directory.

You can use ``sniffer --help`` for options And like autonose_, you can pass the nose 
arguments: ``-x--with-doctest`` or ``-x--config``.

The problem with autonose_, is that the autodetect can be slow to detect changes. This is due
to the pure python implementation - manually walking through the file system to see what's
changed. Although the default install of sniffer shares the same problem, installing a
third-party library can help fix the problem. The library is dependent on your operating system:

 - If you use **Linux**, you'll need to install pyinotify_.
 - If you use **Windows**, you'll need to install pywin32_.
 - If you use **Mac OS X** 10.5+ (Leopard), you'll need to install MacFSEvents_.

.. _nose: http://code.google.com/p/python-nose/
.. _easy_install: http://pypi.python.org/pypi/setuptools
.. _pip: http://pypi.python.org/pypi/pip
.. _autonose: http://github.com/gfxmonk/autonose
.. _pyinotify: http://trac.dbzteam.org/pyinotify
.. _pywin32: http://sourceforge.net/projects/pywin32/
.. _MacFSEvents: http://pypi.python.org/pypi/MacFSEvents/0.2.1

Advanced Usage
------

Don't want to run nose? You can do whatever you really want. Create a scent.py file in
your current working directory. Here's an example of what you can do so far::

  from sniffer.api import * # import the really small API
  import os, termstyle
  
  # you can customize the pass/fail colors like this
  pass_fg_color = termstyle.green
  pass_bg_color = termstyle.bg_default
  fail_fg_color = termstyle.red
  fail_bg_color = termstyle.bg_default
  
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

And that's it. Nothing too fancy shmanshe. You can have multiple file_validator and
runnable decorators if you want.

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

Using the FileSystem monitoring code
------------------------------------

If you simply want to use the file system monitor code, ``import sniffer.Scanner``. Behind
the scenes, the library will figure out what libraries are available to use and which
monitor technique to use.

Right now, this is lacking some documentation, but here's a small example.

Creating the scanner is simple::

  from sniffer import Scanner

  paths = ('/path/to/watch/', '/another/path')
  scanner = Scanner(paths)

Here we pass a tuple of paths to monitor. Now we need to get notification when events occur::

  # when file is created (function accepts the filepath string)
  scanner.observe('created', file_created_func)

  # when file is modified (function accepts the filepath string)
  scanner.observe('modified', file_modified_func)

  # when file is deleted (function accepts the filepath string)
  scanner.observe('deleted', file_deleted_func)

  def init_func(filename):
      print "Scanner started listening"
  # when scanner.loop() is called
  scanner.observe('init', init_func)

In addition, we can use the same function to listen to multiple events::

  # listen to multiple events
  def output_file(filename):
      print "Triggered", filename
  scanner.observe(('created', 'modified', 'deleted'), output_file)

Finally, we start our blocking loop::

  # blocks
  scanner.loop()

Current Issues
==============

For linux, there is an exception that is sometimes thrown when terminating.

Currently the program only looks for changes in the current working directory. This isn't the
best solution: it doesn't understand how changes to your source code affects it.
