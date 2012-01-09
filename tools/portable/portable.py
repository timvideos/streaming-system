#!/usr/bin/python
#
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et sts=4 ai:

import gobject
import pygtk
pygtk.require('2.0')
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

        battery = xml.get_page("battery")
        assistant.append_page(battery)
        assistant.set_page_title(battery, "Power Setup")
        assistant.set_page_type(battery, gtk.ASSISTANT_PAGE_CONTENT)
        assistant.set_page_complete(battery, True)

        network = xml.get_page("network")
        assistant.append_page(network)
        assistant.set_page_title(network, "Network Setup")
        assistant.set_page_type(network, gtk.ASSISTANT_PAGE_CONTENT)
        assistant.set_page_complete(network, True)

        presentation = xml.get_page("presentation")
        assistant.append_page(presentation)
        assistant.set_page_title(presentation, "Presentation Capture Setup")
        assistant.set_page_type(presentation, gtk.ASSISTANT_PAGE_CONTENT)
        assistant.set_page_complete(presentation, True)

        camera = xml.get_page("camera")
        assistant.append_page(camera)
        assistant.set_page_title(camera, "Camera Capture Setup")
        assistant.set_page_type(camera, gtk.ASSISTANT_PAGE_CONTENT)
        assistant.set_page_complete(camera, True)

        interaction = xml.get_page("interaction")
        assistant.append_page(interaction)
        assistant.set_page_title(interaction, "Interaction Setup")
        assistant.set_page_type(interaction, gtk.ASSISTANT_PAGE_CONTENT)
        assistant.set_page_complete(interaction, True)

        audio_inroom = xml.get_page("audio-inroom")
        assistant.append_page(audio_inroom)
        assistant.set_page_title(audio_inroom, "Inroom Audio Setup")
        assistant.set_page_type(audio_inroom, gtk.ASSISTANT_PAGE_CONTENT)
        assistant.set_page_complete(audio_inroom, True)

        audio_standalone = xml.get_page("audio-standalone")
        assistant.append_page(audio_standalone)
        assistant.set_page_title(audio_standalone, "Standalone Audio Setup")
        assistant.set_page_type(audio_standalone, gtk.ASSISTANT_PAGE_CONTENT)
        assistant.set_page_complete(audio_standalone, True)

        # and the window
        assistant.show_all()
        assistant.connect("close", gtk.main_quit, "WM destroy")
        assistant.fullscreen()

        self.xml.builder.connect_signals(self)
        self.timer_id = gobject.timeout_add(1000, self.update_power)

    def update_power(self, evt=None):
        if self.timer_id is not None:
            pic = self.xml.builder.get_object('battery-pic')
            pic.set_from_file(['img/photos/power-disconnected.jpg', 'img/photos/power-connected.jpg'][platform.get_ac_status()])
            return True
        return False


    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()


if __name__ == "__main__":
    app = App()
    app.main()
