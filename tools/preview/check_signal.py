import os
import sys
import errno
import requests
import shutil
import subprocess
config_path = os.path.realpath(os.path.dirname(__file__)+"../..")
if config_path not in sys.path:
    sys.path.append(config_path)
import config
from gi.repository import Gst

Gst.init(None)

loaded_config = config.config_load()
channels = loaded_config.groups()


def generate_thumb(channel, url):
    pipeline = "uridecodebin uri=%s \
                ! videoconvert \
                ! videoscale \
                ! video/x-raw,width=300,height=217 \
                ! pngenc snapshot=true \
                ! filesink location=/srv/%s/snapshot.png" % (url, channel)

    pipeline = Gst.parse_launch(pipeline)
    bus = pipeline.get_bus()
    pipeline.set_state(Gst.State.PLAYING)
    bus.poll(Gst.MessageType.EOS, Gst.CLOCK_TIME_NONE)
    pipeline.set_state(Gst.State.NULL)
    print "%s snapshot generated" % channel

for channel in channels:
    try:
        os.makedirs("/srv/%s" % channel)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

for channel in channels:
    os.chdir("/srv")
    encoder_url = loaded_config.config(channel)["flumotion-encoder"]
    url = "http://%s:8081/loop.raw" % encoder_url
    print "\nscanning %s" % channel

    try:
        r = requests.head(url, stream=True)
    except:
        print "%s is down..." % channel
        continue

    if r.headers["content-type"] == "None":
        print "NO SIGNAL in %s" % channel
        try:
            shutil.copy("./no_signal.png",
                        "/srv/%s/latest.png" % channel)
        except Exception, e:
            raise shutil.Error("Unable to copy no_signal.png\n%s" % e)
    else:
        os.chdir("/srv/%s" % channel)
        generate_thumb(channel, url)
        subprocess.check_call(["pngcrush", "-q", "snapshot.png", "latest.png"])
