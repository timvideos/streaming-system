#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import sys
import threading

import gobject
import pygtk
pygtk.require('2.0')

import gst
import gtk
import gtk.glade

from twisted.internet import error, defer, reactor
from twisted.python import log as twistedlog

import portable_platform


class PortableXML(object):
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("portable.xml")

    def get_page(self, name):
        window = self.builder.get_object(name)
        child = window.get_children()[0]
        window.remove(child)
        return child

    def get_object(self, *args, **kw):
        return self.builder.get_object(*args, **kw)


class SetUpPage(object):
    interval = 1000

    def __init__(self, assistant, xml):
        self.assistant = assistant
        self.xml = xml

        self.page = xml.get_page(self.xmlname)

        self.index = assistant.append_page(self.page)
        assistant.set_page_title(self.page, self.title)
        assistant.set_page_type(self.page, gtk.ASSISTANT_PAGE_CONTENT)
        assistant.set_page_complete(self.page, False)

        self.timer = None
        assistant.connect("prepare", self.on_prepare)

    def on_prepare(self, assistant, page):
        if page == self.page:
            print "on_prepare", self
            self.timer = gobject.timeout_add(self.interval, self.update)
            self.on_show()
        else:
            self.on_unprepare()

    def update(self):
        pass

    def on_unprepare(self):
        self.timer = None

    def on_show(self):
        self.update()

    def focus_forward(self):
        def callback(widget, label):
            if hasattr(widget, 'get_children'):
                for child in widget.get_children():
                    if hasattr(child, 'get_label') and child.get_label() == label:
                        child.grab_focus()
        self.assistant.forall(callback, 'gtk-go-forward')


class BatteryPage(SetUpPage):
    xmlname = "battery"
    title = "Power Setup"

    def update(self, evt=None):
        if self.timer is not None:
            pic = self.xml.get_object('battery-pic')
            text = self.xml.get_object('battery-instructions')

            if portable_platform.get_ac_status():
                pic.set_from_file('img/photos/power-connected.jpg')
                text.set_label('Power has been connected, yay!')
                self.assistant.set_page_complete(self.page, True)
                self.focus_forward()
            else:
                pic.set_from_file('img/photos/power-disconnected.jpg')
                text.set_label('Please connect the power cable.')
                self.assistant.set_page_complete(self.page, False)
            return True
        return False


class NetworkPage(SetUpPage):
    xmlname = "network"
    title = "Network Setup"

    def update(self, evt=None):
        if self.timer is not None:
            self.check_network()
            return True
        return False

    def check_network(self):
        if not getattr(self, 'checking', False):
            self.checking = True
            def callback(self=self):
                import gobject
                if portable_platform.get_network_status():
                    gobject.idle_add(self.network_connected)
                else:
                    gobject.idle_add(self.network_disconnected)
                self.checking = False

            t = threading.Thread(target=callback)
            t.start()

    def network_connected(self):
        text = self.xml.get_object('network-instructions')
        text.set_label('')
        self.assistant.set_page_complete(self.page, True)
        self.focus_forward()

    def network_disconnected(self):
        text = self.xml.get_object('network-instructions')
        text.set_label('Please turn on the Telstra Next-G Elite Device. (Power button is shown below.)')
        self.assistant.set_page_complete(self.page, False)


class VideoPage(SetUpPage):

    def __init__(self, *args, **kw):
        self.player = None
        SetUpPage.__init__(self, *args, **kw)

        video = self.xml.get_object(self.video_component)
        video.unset_flags(gtk.DOUBLE_BUFFERED)
        video.connect("expose-event", self.on_expose)
        video.connect("map-event", self.on_map)
        video.connect("unmap-event", self.on_unprepare)

    def update(self, evt=None):
        if self.timer is not None:
            print self, "update"
            if self.player is not None:
                print "Getting player state"
                if (gst.STATE_CHANGE_SUCCESS, gst.STATE_PLAYING) == self.player.get_state(timeout=1)[:-1]:
                    print "After"
                    self.assistant.set_page_complete(self.page, True)
                    return True
                print "After"

            self.assistant.set_page_complete(self.page, False)
            return True

        return False

    def on_expose(self, *args):
        video = self.xml.get_object(self.video_component)
        # Force the window to be realized
        video.window.xid

    def on_map(self, *args):
        video = self.xml.get_object(self.video_component)
        self.video_xid = video.window.xid

        self.player = gst.parse_launch(self.video_pipeline)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

        self.player.set_state(gst.STATE_PLAYING)

    def on_unprepare(self, *args):
        SetUpPage.on_unprepare(self)

        if self.player is not None:
            self.player.set_state(gst.STATE_NULL)
            while (gst.STATE_CHANGE_SUCCESS, gst.STATE_NULL) != self.player.get_state()[:-1]:
                pass
            sys.stdout.flush()
            self.player = None

    def on_message(self, bus, message):
        print message
        t = message.type
        if t == gst.MESSAGE_EOS:
            print "End of stream!?"
            self.player.set_state(gst.STATE_NULL)

        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.player.set_state(gst.STATE_NULL)

    def on_sync_message(self, bus, message):
        print message
        if message.structure is None:
            return
        message_name = message.structure.get_name()
        if message_name == "prepare-xwindow-id":
            message.src.set_property("force-aspect-ratio", True)
            message.src.set_xwindow_id(self.video_xid)


class PresentationPage(VideoPage):
    xmlname = "presentation"
    title = "Presentation Capture Setup"

    # FIXME: Need to keep this in sync with producer-firewire in flumotion-config/collector-portable.xml
    video_pipeline = """\
v4l2src device=/dev/video1 !
image/jpeg,width=640,height=480,framerate=(fraction)24/1 !
jpegdec !
videocrop left=80 right=80 top=0 bottom=0 !
videoscale !
autovideosink
"""
    video_component = 'presentation-preview'


class CameraPage(VideoPage):
    xmlname = "camera"
    title = "Presenter Capture Setup"

    # FIXME: Need to keep this in sync with composite-video the flumotion-config/collector-portable.xml
    video_pipeline = """\
v4l2src device=/dev/video1 !
image/jpeg,width=640,height=480,framerate=(fraction)24/1 !
jpegdec !
videocrop left=80 right=80 top=0 bottom=0 !
videoscale !
autovideosink
"""
    video_component = 'camera-preview'


class AudioPage(SetUpPage):
    xmlname = "audio-inroom"
    title = "Inroom Audio Setup"

    def __init__(self, flumotion, *args):
        self.flumotion = flumotion
        SetUpPage.__init__(self, *args)

        from flumotion.common import log
        log.init()

        from flumotion.common import connection
        from flumotion.twisted import pb

        from flumotion.admin import admin
        self.medium = admin.AdminModel()

        i = connection.PBConnectionInfo(
            "127.0.0.1", 7531, True, pb.Authenticator(username='user', password='test'))
        d = self.medium.connectToManager(i)
        d.addCallback(self.connected)
        d.addErrback(twistedlog.err)

    def connected(self, *args):
        d = self.medium.callRemote('getPlanetState')
        d.addCallback(self.planet_state)
        d.addErrback(twistedlog.err)
        return d

    def planet_state(self, result):

        from flumotion.monitor.nagios import util
        componentState = util.findComponent(result, '/default/producer-firewire')
        from flumotion.common import componentui

        import volume_monitor
        self.volume_monitor = volume_monitor.VolumeMonitor(self.medium, componentState)

        d = self.medium.componentCallRemote(componentState, 'getUIState')
        d.addCallback(self.uistate)
        return d

    def uistate(self, uistate):
        print "uistate!, creating volume_monitor"
        print 'uistate', uistate
        l = uistate.keys()
        l.sort()
        print 'Properties:'
        for p in l:
            print '- %s - %s' % (p, uistate.get(p))
        uistate.addListener(
            self, set_=self.stateSet, append=self.stateAppend,
            remove=self.stateRemove)
        self.uistate = uistate

        self.volume_monitor.setUIState(uistate)

        self.volume_monitor.wtree.get_widget('window1').show()

    def stateSet(self, object, key, value):
        print "set", object, key, value

    def stateAppend(self, object, key, value):
        print "append", object, key, value

    def stateRemove(self, object, key, value):
        print "remove", object, key, value

    def disconnected(self, *args):
        print "Disconnected", args



class App(object):

    # This is a callback function. The data arguments are ignored
    # in this example. More on callbacks below.
    def hello(self, widget, data=None):
        print "Hello World"

    def delete_event(self, widget, event, data=None):
        # If you return FALSE in the "delete_event" signal handler,
        # GTK will emit the "destroy" signal. Returning TRUE means
        # you don't want the window to be destroyed.
        # This is useful for popping up 'are you sure you want to quit?'
        # type dialogs.
        print "delete event occurred"

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    def __init__(self):
        xml = PortableXML()
        self.xml = xml

        assistant = gtk.Assistant()
        self.assistant = assistant

        battery = BatteryPage(assistant, xml)
        network = NetworkPage(assistant, xml)
        presentation = PresentationPage(assistant, xml)
        camera = CameraPage(assistant, xml)

        # Setup the Flumotion connection object
        from flumotion.common import log
        log.init()
        audio_inroom = AudioPage(None, assistant, xml)

        interaction = xml.get_page("interaction")
        assistant.append_page(interaction)
        assistant.set_page_title(interaction, "Interaction Setup")
        assistant.set_page_type(interaction, gtk.ASSISTANT_PAGE_CONTENT)
        assistant.set_page_complete(interaction, False)

        audio_standalone = xml.get_page("audio-standalone")
        assistant.append_page(audio_standalone)
        assistant.set_page_title(audio_standalone, "Standalone Audio Setup")
        assistant.set_page_type(audio_standalone, gtk.ASSISTANT_PAGE_CONTENT)
        assistant.set_page_complete(audio_standalone, False)

        # and the window
        assistant.show_all()
        assistant.connect("close", gtk.main_quit, "WM destroy")
        assistant.fullscreen()


    def main(self):
        gtk.gdk.threads_init()
        reactor.run()


def main(args):
    app = App()
    app.main()
