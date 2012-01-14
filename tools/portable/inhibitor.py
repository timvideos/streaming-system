#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

# Code taken from http://www.devtech.com/inhibitapplet

import dbus

class Inhibitor(object):
    '''
    Uses the Gnome SessionManager D-Bus interface to inhibit session idling and other inhibitable activities.

    References:

    http://svn.gnome.org/viewvc/gnome-session/trunk/gnome-session/org.gnome.SessionManager.xml?view=markup
    http://blogs.gnome.org/hughsie/2009/01/28/inhibits-and-the-new-world-order/
    http://git.gnome.org/browse/gnome-power-manager/tree/applets/inhibit/inhibit-applet.c?h=gnome-2-32
    http://git.gnome.org/browse/gnome-session/tree/gnome-session/gsm-manager.c
    http://en.wikibooks.org/wiki/Python_Programming/Dbus
    '''

    LOGGING_OUT=1
    USER_SWITCHING=2
    SUSPENDING=4
    IDLE=8

    def __init__(self):
        self.bus = dbus.SessionBus()
        self.session_manager = self.bus.get_object("org.gnome.SessionManager","/org/gnome/SessionManager")
        self.session_manager_interface = dbus.Interface(self.session_manager, "org.gnome.SessionManager")

    def inhibit(self, flags = IDLE, app_id="PyInhibit", toplevel_xid=0, reason="OnDemand"):
        self.uninhibit()
        if 0 < flags <= (Inhibitor.LOGGING_OUT + Inhibitor.USER_SWITCHING + Inhibitor.SUSPENDING + Inhibitor.IDLE):
            self.cookie = self.session_manager_interface.Inhibit(app_id, toplevel_xid, reason, flags)

    def uninhibit(self):
        if "cookie" in self.__dict__:
            self.session_manager_interface.Uninhibit(self.cookie)
            del self.cookie

    def isInhibited(self, flags):
        return self.session_manager_interface.IsInhibited(flags)

    def introspect(self):
        introspector = dbus.Interface(self.session_manager, dbus.INTROSPECTABLE_IFACE)
        interface = introspector.Introspect()
