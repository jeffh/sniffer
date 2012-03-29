"""
Notifiers for sniffer by Nathan Dotz - 2012
http://github.com/sleepynate

Notifiers were originally part of:
GitMon - The Git Repository Monitor
Copyright (C) 2010  Tomas Varaneckas
http://www.varaneckas.com

This is a derivative work, go give Tomas props!

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import subprocess
if sys.platform.startswith('darwin') or sys.platform.startswith('win'):
    import Growl
else:
    import pynotify

class Notifier(object):

    def notify(self, title=None, message=None, image=None):
        pass

    @classmethod
    def create(cls):
        """Returns singleton instance of given notifier type"""
        try:
            Growl.__class__
            return GrowlNotifier.instance()
        except NameError:
            return LibnotifyNotifier.instance()

class LibnotifyNotifier(Notifier):

    inst = None

    @classmethod
    def instance(cls):
        if not LibnotifyNotifier.inst:
            LibnotifyNotifier.inst = LibnotifyNotifier()
        return LibnotifyNotifier.inst

    def notify(self, title, message, image=None):
        if not pynotify.is_initted():
            pynotify.init('sniffer')
        if image:
            image = 'file://%s' % image
            notification = pynotify.Notification(title, message, image)
        else:
            notification = pynotify.Notification(title, message)
        if not notification.show():
            print "Failed showing python libnotify notification"

class GrowlNotifier(Notifier):

    inst = None

    @classmethod
    def instance(cls):
        if not GrowlNotifier.inst:
            GrowlNotifier.inst = GrowlNotifier()
        return GrowlNotifier.inst

    def notify(self, title, message, image=None):
        if image:
            image = Growl.Inmage.imageFromPath(image)
        sticky = bool(int(self.config['growl.sticky.notifications']))
        growl = Growl.GrowlNotifier(applicationName='sniffer', \
                applicationIcon=image, \
                notifications=['update'], \
                defaultNotifications=['update'])
        if not hasattr(self, 'registered'):
            growl.register()
            self.registered = True
        growl.notify('update', title, message, icon=image, sticky=sticky)
