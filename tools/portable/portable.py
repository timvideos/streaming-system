#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import ConfigParser
import subprocess
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
        
from flumotion.admin import admin
from flumotion.common import log
from flumotion.common import connection
from flumotion.common import componentui
from flumotion.common.planet import moods
from flumotion.monitor.nagios import util
from flumotion.twisted import pb

import inhibitor
import portable_platform

CONFIG = ConfigParser.ConfigParser()
CONFIG.read(['config.ini'])

FAKE=CONFIG.getboolean('config', 'fake')


class PortableXML(object):
    def __init__(self):
        self.builder = gtk.Builder()
        self.builder.add_from_file("portable.glade")

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
            self.timer = gobject.timeout_add(self.interval, self.update)
            self.on_show()
        else:
            self.on_unshow()

    def update(self):
        pass

    def on_unshow(self):
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

            if portable_platform.get_ac_status() or FAKE:
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
                if portable_platform.get_network_status() or FAKE:
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
        video.connect("unmap-event", self.on_unshow)

    def update(self, evt=None):
        if self.timer is not None:
            if self.player is not None:
                if (gst.STATE_CHANGE_SUCCESS, gst.STATE_PLAYING) == self.player.get_state(timeout=1)[:-1] or FAKE:
                    self.assistant.set_page_complete(self.page, True)
                    self.focus_forward()
                    return True

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

    def on_unshow(self, *args):
        SetUpPage.on_unshow(self)

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
dv1394src guid=%s !
queue leaky=2 max-size-time=1000000000 !
dvdemux name=demux !
dvdec !
videoscale !
autovideosink
""" % CONFIG.get('firewire', 'guid')
    video_component = 'presentation-preview'


class CameraPage(VideoPage):
    xmlname = "camera"
    title = "Presenter Capture Setup"

    # FIXME: Need to keep this in sync with composite-video the flumotion-config/collector-portable.xml
    video_pipeline = """\
v4l2src device=%s !
image/jpeg,width=640,height=480,framerate=(fraction)24/1 !
jpegdec !
videocrop left=80 right=80 top=0 bottom=0 !
videoscale !
autovideosink
""" % CONFIG.get('camera', 'device')
    video_component = 'camera-preview'


class AudioPage(SetUpPage):
    def __init__(self, flumotion, *args):
        self.flumotion = flumotion

        SetUpPage.__init__(self, *args)

        self.volume_monitor = None

    def on_show(self):
        config = open('../flumotion-config/collector-portable.xml').read()
        camera_device = CONFIG.get('camera', 'device')
        firewire_guid = CONFIG.get('firewire', 'guid')

        d = self.flumotion.medium.loadConfiguration(config % locals())
        
        def loaded(*args):
            print "Full configuration loaded."
            self.update()

        d.addCallback(loaded)
        d.addErrback(twistedlog.err)

    def update(self, evt=None):
        if self.timer is None:
            return False

        self.set_state()
        return True

    def set_state(self):
        
        def planet_callback(uistate, self=self):
            component = util.findComponent(uistate, '/default/producer-firewire')

            if self.volume_monitor is None:
                import volume_monitor
                parent_widget = self.xml.get_object(self.box)
                self.volume_monitor = volume_monitor.VolumeMonitor(self.flumotion.medium, component, force_channels=1)

                volume_widget = self.volume_monitor.widget
                old_parent = volume_widget.get_parent()
                if old_parent:
                    old_parent.remove(volume_widget)
                parent_widget.pack_start(volume_widget)

            if moods.get(component.get('mood')) is not moods.happy:
                return

            def component_callback(firewire_uistate, self=self):
                if self.volume_monitor.state is not None:
                    return
                self.volume_monitor.setUIState(firewire_uistate)
                self.assistant.set_page_complete(self.page, True)
                self.focus_forward()

            d = self.flumotion.medium.componentCallRemote(component, 'getUIState')
            d.addCallback(component_callback)

        d = self.flumotion.get_planet_state()
        d.addCallback(planet_callback)

    def on_unshow(self):
        self.flumotion.connected()
        self.volume_monitor = None


class AudioInRoomPage(AudioPage):
    xmlname = "audio-inroom"
    title = "Inroom Audio Setup"
    box = "audio-inroom-box"


class AudioStandAlonePage(AudioPage):
    xmlname = "audio-standalone"
    title = "Stand Alone Audio Setup"
    box = "audio-standalone-box"



class FlumotionConnection(object):

    def __init__(self):
        log.init()

        self.medium = admin.AdminModel()

        i = connection.PBConnectionInfo(
            "127.0.0.1", 7531, True, pb.Authenticator(username='user', password='test'))
        d = self.medium.connectToManager(i)
        d.addCallback(self.connected)
        d.addErrback(twistedlog.err)

    def connected(self, *args):
        print "Connected to flumotion."
        d = self.medium.cleanComponents()
        
        def loaded(*args):
            print "Configuration cleared."

        d.addCallback(loaded)
        d.addErrback(twistedlog.err)
        return d

    def get_planet_state(self):
        d = self.medium.callRemote('getPlanetState')
        d.addErrback(twistedlog.err)
        return d


class App(object):

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        subprocess.call('sudo /etc/init.d/flumotion restart', shell=True)

        # Stop the screensaver and screen blanking
        self.inhibitor = inhibitor.Inhibitor()
        self.inhibitor.inhibit(reason="Video streaming!")

        flumotion = FlumotionConnection()

        xml = PortableXML()
        self.xml = xml

        assistant = gtk.Assistant()
        self.assistant = assistant

        battery = BatteryPage(assistant, xml)
        network = NetworkPage(assistant, xml)
        presentation = PresentationPage(assistant, xml)
        camera = CameraPage(assistant, xml)

        audio_inroom = AudioInRoomPage(flumotion, assistant, xml)
        #audio_standalone = AudioStandAlonePage(flumotion, assistant, xml)

        #interaction = xml.get_page("interaction")
        #assistant.append_page(interaction)
        #assistant.set_page_title(interaction, "Interaction Setup")
        #assistant.set_page_type(interaction, gtk.ASSISTANT_PAGE_CONTENT)
        #assistant.set_page_complete(interaction, False)

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
