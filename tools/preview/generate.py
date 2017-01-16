import errno
import os
import requests
import shutil
import subprocess
import sys
import time
import traceback

mydir = os.path.dirname(__file__)
config_path = os.path.realpath(mydir+"../..")
if config_path not in sys.path:
    sys.path.append(config_path)
import config
from gi.repository import Gst

Gst.init(None)

loaded_config = config.config_load()
channels = loaded_config.groups()


def generate_thumb(dst, url):
    print "%s snapshot starting" % dst
    pipeline = "uridecodebin uri=\"%s\" \
                ! videoconvert \
                ! videoscale \
                ! video/x-raw,width=300,height=168 \
                ! pngenc snapshot=true \
                ! filesink location=%s" % (url, dst)
    assert not os.path.exists(dst)
    p = subprocess.Popen("gst-launch-1.0 "+pipeline, shell=True)

    start = time.time()
    while p.poll() == None and (time.time()-start) < 5.0:
        print "Waiting for cmd..."
        time.sleep(1)
    while p.poll() == None:
        p.kill()
        time.sleep(1)
    assert os.path.exists(dst)
    return
    print pipeline
    pipeline = Gst.parse_launch(pipeline)
    bus = pipeline.get_bus()
    pipeline.set_state(Gst.State.PLAYING)
    bus.poll(Gst.MessageType.EOS, Gst.CLOCK_TIME_NONE)
    pipeline.set_state(Gst.State.NULL)
    #FIXME: This should return true if the preview was generated
    print "%s snapshot generated" % dst

# channels = ['test']
no_signal = os.path.realpath(os.path.join(mydir, 'no_signal.png'))
print("No signal image: %s" % no_signal)

TOP_DIR="/srv/preview/%s"
for channel in channels:
    try:
        os.makedirs(TOP_DIR % channel)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

for channel in channels:
    os.chdir(TOP_DIR % "")
    youtube_id = loaded_config.config(channel)["youtube"]
    url = "https://www.youtube.com/watch?v=%s" % youtube_id
    print "\nscanning %s" % channel

    snapfile = (TOP_DIR % channel) + "/snapshot.png"
    lfile = (TOP_DIR % channel) + "/latest.png"
    try:
        dash_url = subprocess.check_output("~/bin/youtube-dl -g %s" % url, shell=True).strip()
        print dash_url

        os.chdir(TOP_DIR % channel)
        if os.path.exists(snapfile):
            os.unlink(snapfile)
        generate_thumb(snapfile, dash_url)
        assert os.path.exists(snapfile)
        assert len(open(snapfile).read())
        subprocess.check_call(["pngcrush", "-q", snapfile, lfile])
        assert os.path.exists(lfile)
        assert len(open(lfile).read())
    except (AssertionError, Exception) as e:
        print "-"*75
        print e
        traceback.print_exc()
        print "-"*75
        shutil.copy(no_signal, lfile)
