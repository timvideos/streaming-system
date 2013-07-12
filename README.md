
# The Tim Video's Streaming System

For how the streaming system fits into the overall TimVideos.us projects, look
at the following diagram:
![TimVideos.US overall Diagram](https://docs.google.com/drawings/d/1crkdqukOAV9Alq9BOMFucDmwc_HD6qnJ4OF5MJpkrLg/pub?w=960&h=720)

For how the streaming system overall looks at the following diagram;
![Streaming System overall Diagram](https://docs.google.com/drawings/d/1ZN5uqd-fo62e0IZSzuOSo6YadRY_n7umkUThmqckACA/pub?w=960&h=720)


## What is Tim Video's?

Tim Video's is a collection of tools for live streaming conferences and user
groups. It includes both software and hardware for both the recording and
viewing sides.

It has been used with conferences like PyCon US and Linux.conf.au and at user
groups like Sydney Linux User Group and Sydney Python User Group.

# Parts

 * **website** - The actual website people end up seeing/going too. Uses
   jwplayer and django. The website is split into two parts;

    * The **frontend** is the UI which provides the tool and feel of the
      system. This system is stateless and requires no databases.

    * The **tracker** is the backend which keeps track of stats about the
      system. It is only accessed through a JSON API.

 * **tools** - Mish mash of parts of the streaming system.

    * **flumotion**, **flumotion-ugly** and **flumotion-fragmented-streaming**
      oftware which does the actual streaming.

    * **flumotion-config** - Example flumotion configuration files and some
      tools to push the configurations out to systems. Useful for conferences
      where you are managing a lot of encoders/collectors.

    * **flumotion-extra** - Website controller of flumotion (replaces the GTK
      tool).

    * **portable** - Code to deal with the portable "in a box" solution.

    * **register** - Tool which reports an encoder (and how many clients are
      using the encoder - for load balancing) to tracker website.

    * **watchdog** - Tool which restarts bad flumotion components and systems.

    * **fluhelper** - Rewrite of the register and watchdog tools into one
      unified system.

    * **irclog2html** - Scripts for converting irclogs into the HTML format
      needed by the website.

    * **preview** - Scripts for capturing preview images from the video
      streams.

    * **setup** - Set up a server with the timvideo tools. 
      *Really needs to be replaced with proper configuration management such as puppet or chef.*

    * **youtube** - Upload recorded videos to YouTube channel.

## Related Projects

### gst-switch

 * Mailing List: gst-switch@googlegroups.com
 * Code: http://github.com/timvideos/gst-switch

gst-switch is a project to replace the wonderful but aging
[dv-switch tool][dvswitch] with a modern system based on top of
 [gstreamer][gst].

 [dvswitch]: http://dvswitch.alioth.debian.org/wiki/
 [gst]: http://gstreamer.freedesktop.org/

### HDMI2USB

A HDMI stream capturing system which connects with PC and will appears as a
video/web camera. Act as a passthru system.

Design to be a high definition, digital replacement for TwinPac.

Initial design is based on Digilent Atlys. Custom boards coming soon.


 * Mailing List: hdmi2usb@googlegroups.com
 * Code: http://github.com/timvideos/hdmi2usb

[![githalytics.com alpha](https://cruel-carlota.pagodabox.com/9f3b89d7feac43bbbd791b9313d2e7e3 "githalytics.com")](http://githalytics.com/github.com/timvideos)
