Overview
========

``sniffer`` is a autotest tool for Python_ using the nosetest_ library.

Sniffer will automatically re-run tests if your code changes. And with another third-party
library (see below), the CPU usage of file system monitoring is reduced in comparison
to pure-python solutions. However, sniffer will still work without any of those libraries.

.. _Python: http://python.org/
.. _nosetest: http://code.google.com/p/python-nose/

Usage
-----

To install::

  pip install nose
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

**As a word of warning**, Windows and OSX libraries are *untested* as of now. This is because I
haven't gotten around to testing in Windows, and I don't have a Mac :(.

.. _nose: http://code.google.com/p/python-nose/
.. _easy_install: http://pypi.python.org/pypi/setuptools
.. _pip: http://pypi.python.org/pypi/pip
.. _autonose: http://github.com/gfxmonk/autonose
.. _pyinotify: http://trac.dbzteam.org/pyinotify
.. _pywin32: http://sourceforge.net/projects/pywin32/
.. _MacFSEvents: http://pypi.python.org/pypi/MacFSEvents/0.2.1


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

After subclassing, set sniffer_cls parameter to your custom class when calling run or main.

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

  # when file is created
  scanner.observe('created', lambda path: print "Created", path)

  # when file is modified
  scanner.observe('modified', lambda path: print "Modified", path)

  # when file is deleted
  scanner.observe('deleted', lambda path: print "Deleted", path)

  # when scanner.loop() is called
  scanner.observe('init',    lambda: print "Scanner started listening.")

In addition, we can use the same function to listen to multiple events::

  # listen to multiple events
  scanner.observe(('created', 'modified', 'deleted'), lambda path: "Triggered:", path)

Finally, we start our blocking loop::

  # blocks
  scanner.loop()

Current Issues
==============

Being relatively new, there are bound to be bugs. Most notable is third-party libraries.
Only the Linux install was tested (being in Ubuntu), so Windows & OSX implementations were
done *without testing*. Patches are welcomed though :)

For linux, there is an exception that is sometimes thrown when terminating.

Currently the program only looks for changes in the current working directory. This isn't the
best solution: it doesn't understand how changes to your source code affects it.
