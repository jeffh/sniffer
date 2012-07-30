import sys


class NullEmitter(object):
    "Emitter that does nothing."
    def success(self, sniffer):
        pass
    def failure(self, sniffer):
        pass

class PrinterEmitter(object):
    "Simply emits exit status info to the console/terminal."
    def success(self, sniffer):
        print sniffer.pass_colors['bg'](sniffer.pass_colors['fg']("In good standing"))

    def failure(self, sniffer):
        print sniffer.fail_colors['bg'](sniffer.fail_colors['fg']("Failed - Back to work!"))

try:
    import pynotify
    class PynotifyEmitter(object):
        "Emits exit status info to libnotify"
        def __init__(self):
            pynotify.init('Sniffer')

        def success(self, sniffer):
            pynotify.Notification('Sniffer', 'In good standing').show()

        def failure(self, sniffer):
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
                print >>sys.stderr, "Failed to connect to growl! :("
                self.growl = None

        def success(self, sniffer):
            if self.growl:
                self.growl.notify(
                    noteType="Passes",
                    title="Sniffer",
                    description="In good standing!",
                    sticky=False,
                    priority=1,
                )

        def failure(self, sniffer):
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


class Broadcaster(object):
    def __init__(self, *emitters):
        self.emitters = emitters

    def success(self, sniffer):
        for emit in self.emitters:
            emit.success(sniffer)

    def failure(self, sniffer):
        for emit in self.emitters:
            emit.failure(sniffer)


broadcaster = Broadcaster(
    PrinterEmitter(),
    GrowlEmitter(),
    PynotifyEmitter(),
)
