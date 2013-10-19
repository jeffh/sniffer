from __future__ import print_function
import sys


class NullEmitter(object):
    "Emitter that does nothing."
    def success(self, sniffer, result=None):
        pass
    def failure(self, sniffer, result=None):
        pass

class PrinterEmitter(object):
    "Simply emits exit status info to the console/terminal."
    def success(self, sniffer, result=None):
        print(sniffer.pass_colors['bg'](
            sniffer.pass_colors['fg']("In good standing")))

    def failure(self, sniffer, result=None):
        print(sniffer.fail_colors['bg'](
            sniffer.fail_colors['fg']("Failed - Back to work!")))

try:
    import pynotify
    class PynotifyEmitter(object):
        "Emits exit status info to libnotify"
        def __init__(self):
            pynotify.init('Sniffer')

        def success(self, sniffer, result=None):
            pynotify.Notification('Sniffer', 'In good standing').show()

        def failure(self, sniffer, result=None):
            pynotify.Notification('Sniffer', 'Failed - Back to work!').show()

except ImportError:
    PynotifyEmitter = NullEmitter

try:
    import gntp.notifier
    import socket
    class GrowlEmitter(object):
        "Emits exit status info to growl."
        def __init__(self):
            self.growl = gntp.notifier.GrowlNotifier(
                applicationName="Python Sniffer",
                notifications=["Passes", "Failures"],
                defaultNotifications=["Passes"],
            )
            try:
                self.growl.register()
            except socket.error:
                print("Failed to connect to growl! :(", file=sys.stderr)
                self.growl = None

        def success(self, sniffer, result=None):
            if self.growl:
                self.growl.notify(
                    noteType="Passes",
                    title="Sniffer",
                    description="In good standing!",
                    sticky=False,
                    priority=1,
                )

        def failure(self, sniffer, result=None):
            if self.growl:
                self.growl.notify(
                    noteType="Failures",
                    title="Sniffer",
                    description="Back to work!",
                    sticky=False,
                    priority=1,
                )

except ImportError:
    GrowlEmitter = NullEmitter

try:
    import os
    import subprocess
    import nose
    class TerminalNotifierEmitter(object):
        "Emits exit status info to OS X terminal notifier"

        def success(self, sniffer, result):
            try:
                content = ["terminal-notifier-success",
                           "-title", "Sniffer",
                           "-subtitle", "In good standing",
                           "-message", "%s specifications" % (
                            result.denominator,)]
                with open(os.devnull, "w") as f:
                    subprocess.call(content, stdout=f)
            except Exception, e:
                # we don't really care if this fails
                pass

        def failure(self, sniffer, result):
            try:
                content = ["terminal-notifier-failed",
                           "-title", "Sniffer",
                           "-subtitle", "Failed - Back to work!",
                           "-message", "%s specifications, %s failures" % (
                            result.denominator,
                            result.denominator - result.numerator)]

                with open(os.devnull, "w") as f:
                    subprocess.call(content, stdout=f)
            except Exception, e:
                # we don't really care if this fails
                pass

except ImportError:
    TerminalNotifierEmitter = NullEmitter



class Broadcaster(object):
    def __init__(self, *emitters):
        self.emitters = emitters

    def success(self, sniffer, result=None):
        for emit in self.emitters:
            emit.success(sniffer, result)

    def failure(self, sniffer, result=None):
        for emit in self.emitters:
            emit.failure(sniffer, result)


broadcaster = Broadcaster(
    PrinterEmitter(),
    GrowlEmitter(),
    PynotifyEmitter(),
    TerminalNotifierEmitter()
)
