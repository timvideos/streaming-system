#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import gobject
import pygtk
pygtk.require('2.0')

import gst
import gtk
import gtk.glade

import platform


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
            self.timer = gobject.timeout_add(self.interval, self.update)
            self.update()
        else:
            self.timer = None


class BatteryPage(SetUpPage):
    xmlname = "battery"
    title = "Power Setup"

    def update(self, evt=None):
        if self.timer is not None:
            pic = self.xml.get_object('battery-pic')
            text = self.xml.get_object('battery-instructions')

            if platform.get_ac_status():
                pic.set_from_file('img/photos/power-connected.jpg')
                text.set_label('Power has been connected, yay!')
                self.assistant.set_page_complete(self.page, True)
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
            text = self.xml.get_object('network-instructions')

            if platform.get_network_status():
                text.set_label('')
                self.assistant.set_page_complete(self.page, True)
            else:
                text.set_label('')
                self.assistant.set_page_complete(self.page, False)

            return True
        return False


class PresentationPage(SetUpPage):
    xmlname = "presentation"
    title = "Presentation Capture Setup"

    def __init__(self, *args, **kw):
        self.player = None
        SetUpPage.__init__(self, *args, **kw)

    def update(self, evt=None):
        if self.timer is not None:
            if self.player is not None:
                print self.player.get_state()[1], gst.STATE_PLAYING
                if gst.STATE_PLAYING != self.player.get_state()[1]:
                    self.player.set_state(gst.STATE_PLAYING)
                else:
                    self.assistant.set_page_complete(self.page, True)
                    return True
            else:
                self.create_video()

            self.assistant.set_page_complete(self.page, False)
            return True

        return False

    def create_video(self):
        # Set up the gstreamer pipeline
        # FIXME: Need to keep this in sync with the flumotion-config/collector-portable.xml
        self.player = gst.parse_launch("""\
v4l2src !
videocrop left=80 right=80 top=0 bottom=0 !
videoscale !
autovideosink
""")

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

    def on_message(self, bus, message):
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
            message.src.set_xwindow_id(self.xml.get_object('presentation-preview').window.xid)


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

        camera = xml.get_page("camera")
        assistant.append_page(camera)
        assistant.set_page_title(camera, "Camera Capture Setup")
        assistant.set_page_type(camera, gtk.ASSISTANT_PAGE_PROGRESS)
        assistant.set_page_complete(camera, False)

        interaction = xml.get_page("interaction")
        assistant.append_page(interaction)
        assistant.set_page_title(interaction, "Interaction Setup")
        assistant.set_page_type(interaction, gtk.ASSISTANT_PAGE_PROGRESS)
        assistant.set_page_complete(interaction, False)

        audio_inroom = xml.get_page("audio-inroom")
        assistant.append_page(audio_inroom)
        assistant.set_page_title(audio_inroom, "Inroom Audio Setup")
        assistant.set_page_type(audio_inroom, gtk.ASSISTANT_PAGE_PROGRESS)
        assistant.set_page_complete(audio_inroom, False)

        audio_standalone = xml.get_page("audio-standalone")
        assistant.append_page(audio_standalone)
        assistant.set_page_title(audio_standalone, "Standalone Audio Setup")
        assistant.set_page_type(audio_standalone, gtk.ASSISTANT_PAGE_PROGRESS)
        assistant.set_page_complete(audio_standalone, False)

        # and the window
        assistant.show_all()
        assistant.connect("close", gtk.main_quit, "WM destroy")
        assistant.fullscreen()



    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.gdk.threads_init()
        gtk.main()



if __name__ == "__main__":
    app = App()
    app.main()
