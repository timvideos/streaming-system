# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4
#
# Flumotion - a streaming media server
# Copyright (C) 2004,2005,2006,2007,2008 Fluendo, S.L. (www.fluendo.com).
# All rights reserved.

# This file may be distributed and/or modified under the terms of
# the GNU General Public License version 2 as published by
# the Free Software Foundation.
# This file is distributed without any warranty; without even the implied
# warranty of merchantability or fitness for a particular purpose.
# See "LICENSE.GPL" in the source distribution for more information.

# Licensees having purchased or holding a valid Flumotion Advanced
# Streaming Server license may use this file in accordance with the
# Flumotion Advanced Streaming Server Commercial License Agreement.
# See "LICENSE.Flumotion" in the source distribution for more information.

# Headers in this file shall remain intact.

from gettext import gettext as _

import gtk
import os
import math

# import custom glade handler
from flumotion.ui import glade
from flumotion.ui.fvumeter import FVUMeter


def clamp(x, min, max):
    if x < min:
        return min
    elif x > max:
        return max
    return x


class VolumeMonitor(object):
    logCategory = 'volume'
    gladeFile = 'volume.glade'

    def __init__(self, medium, component, force_channels=100):
        self.medium = medium
        self.component = component
        self.force_channels = force_channels

        self.wtree = gtk.glade.XML("volume_monitor.glade", "window1")

        self.window = self.wtree.get_widget('window1')
        self.uiStateHandlers = None

        self.widget = self.wtree.get_widget('volume-widget')
        self.level_widgets = []
        self._volume_set_label = self.wtree.get_widget('volume-set-label')
        self._volume_set_label.set_text('0')

        # now do the callbacks for the volume setting
        self._hscale = self.wtree.get_widget('volume-set-hscale')
        self._scale_changed_id = self._hscale.connect('value_changed',
                self.cb_volume_set)
        self._hscale.set_sensitive(False)
        # callback for checkbutton
        check = self.wtree.get_widget('volume-set-check')
        check.set_sensitive(False)
        check.connect('toggled', self._check_toggled_cb)
        changeLabel = self.wtree.get_widget('volume-change-label')
        changeLabel.set_sensitive(False)

    def setUIState(self, state):
        if not self.uiStateHandlers:
            self.uiStateHandlers = {'volume-volume': self.volumeSet,
                                    'volume-peak': self.peakSet,
                                    'volume-decay': self.decaySet}
        for k, handler in self.uiStateHandlers.items():
            handler(state.get(k))

        # volume-allow-increase is static for lifetime of component
        # for soundcard it is false, for others that have a gst volume
        # element it is true
        if state.get("volume-allow-increase"):
            check = self.wtree.get_widget('volume-set-check')
            if check is not None:
                check.set_sensitive(True)
        if state.get("volume-allow-set"):
            self._hscale.set_sensitive(True)
            changeLabel = self.wtree.get_widget('volume-change-label')
            if changeLabel is not None:
                changeLabel.set_sensitive(True)

        # Have to keep the state object around so call backs continue to occur.
        self.state = state
        state.addListener(self, set_=self.stateSet, append=None, remove=None)

    def stateSet(self, state, key, value):
        handler = self.uiStateHandlers.get(key, None)
        if handler:
            handler(value)

    def _createEnoughLevelWidgets(self, numchannels):
        """
        This method dynamically creates labels and level meters for channels
        that currently do not have level meters. The glade file no longer
        contains the labels or the level meters. Also the table size in the
        glade file is set to 50 and the widgets inside the table that are
        statically configured have a bottom y of 50 allowing about 23 channels
        in the audio.

        @param numchannels: total number of channels there is volume data for
        """
        if numchannels > len(self.level_widgets):
            totalLevelWidgets = len(self.level_widgets)
            for chan in range(totalLevelWidgets, numchannels):
                levelWidget = FVUMeter()
                levelLabel = gtk.Label()
                if chan == 0 and numchannels > 1:
                    levelLabel.set_text(_("Left channel level:"))
                elif numchannels == 1:
                    levelLabel.set_text(_("Mono channel level:"))
                elif chan == 1:
                    levelLabel.set_text(_("Right channel level:"))
                else:
                    levelLabel.set_text(_("Channel %d level:") % chan)
                levelLabel.set_property("xpad", 0)
                levelLabel.set_property("ypad", 0)
                levelLabel.set_property("xalign", 0)
                levelLabel.set_property("yalign", 0.5)
                levelLabel.set_justify(gtk.JUSTIFY_LEFT)
                self.widget.attach(levelLabel, 0, 1, chan * 2, chan * 2 + 1,
                    xoptions=gtk.FILL, yoptions=0, xpadding=3, ypadding=3)
                self.widget.attach(levelWidget, 0, 1, chan * 2 + 1,
                    chan * 2 + 2, yoptions=gtk.FILL,
                    xpadding=6, ypadding=3)
                levelLabel.show()
                levelWidget.show()
                self.level_widgets.append(levelWidget)

    def peakSet(self, peak):
        if len(peak) > self.force_channels:
            peak = peak[0:self.force_channels]

        if len(peak) > len(self.level_widgets):
            self._createEnoughLevelWidgets(len(peak))
        for i in range(0, len(peak)):
            self.level_widgets[i].set_property('peak',
                clamp(peak[i], -90.0, 0.0))

    def decaySet(self, decay):
        if len(decay) > self.force_channels:
            decay = decay[0:self.force_channels]

        if len(decay) > len(self.level_widgets):
            self._createEnoughLevelWidgets(len(decay))
        for i in range(0, len(decay)):
            self.level_widgets[i].set_property('decay',
                clamp(decay[i], -90.0, 0.0))

    # when volume has been set by another admin client

    def volumeSet(self, volume):
        self._hscale.handler_block(self._scale_changed_id)

        # Ensure that the scale has an adjustment.
        # This is not a proper solution to a problem that
        # can be when switching components, but it avoids an
        # unexpected segfault in set_value which expects
        # range->adjustment to be non-NULL
        self._hscale.get_adjustment()

        self._hscale.set_value(volume)
        dB = "- inf"
        if volume:
            dB = "%2.2f" % (20.0 * math.log10(volume))
        self._volume_set_label.set_text(dB)
        self._hscale.handler_unblock(self._scale_changed_id)

    # run when the scale is moved by user

    def cb_volume_set(self, widget):
        # do something
        volume = self._hscale.get_value()
        #self.volumeSet(volume)
        if self.handlers:
            d = self.effectCallRemote("setVolume", volume)
            d.addErrback(self.setVolumeErrback)

    def setVolumeErrback(self, failure):
        self.warning("Failure %s setting volume: %s" % (
            failure.type, failure.getErrorMessage()))
        return None

    def _update_volume_label(self):
        # update the volume label's dB value
        pass

    # when the "increase volume" checkbutton is toggled

    def _check_toggled_cb(self, widget):
        checked = widget.get_property('active')
        value = self._hscale.get_value()
        if checked:
            self._hscale.set_range(0.0, 4.0)
        else:
            if value > 1.0:
                value = 1.0
            self._hscale.set_range(0.0, 1.0)
        self.volumeSet(value)

    def effectCallRemote(self, methodName, *args, **kwargs):
        return self.medium.componentCallRemote(self.component,
            "effect", self.effectName, methodName, *args, **kwargs)
