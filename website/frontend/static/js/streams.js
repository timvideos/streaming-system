// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

function Streams(server) {
  // Server which is doing the streaming
  this.html5_streams = {
    'modes': ['html5'],
    'hd': [
      { 'file': server+'webcast-high.webm' },
    ],
    'sd': [
      { 'file': server+'webcast-low.webm' },
    ],
    'download': server+'webcast-low.webm'
  };

  this.flash_streams = {
    'modes': ['flash'],
    'hd': [
      { 'bitrate': 800, 'file': server+'webcast-high.flv', 'width': 720 }
    ],
    'sd': [
      { 'bitrate': 300, 'file': server+'webcast-low.flv', 'width': 432 }
    ],
    'download': server+'webcast-low.ogv',
    'extra': {
      'src': '/static/third_party/jwplayer/player.swf'
    }
  };

  this.audio_streams = {
    'modes': ['html5', 'flash'],
    'sd': [
      { 'bitrate': 192, 'file': server+'audio-only.aac', 'width': 100 },
      { 'bitrate': 128, 'file': server+'audio-only.ogg', 'width': 100 },
      { 'bitrate': 48, 'file': server+'audio-only.mp3', 'width': 100 }
    ],
    'download': server+'audio-only.mp3',
    'extra': {
      'src': '/static/third_party/jwplayer/player.swf'
    }
  };

  this.idevice_streams = {
    'modes': ['html5', 'flash'],
    'sd': [
      { 'bitrate': 192, 'file': server+'audio-only.aac', 'width': 100 },
      { 'bitrate': 128, 'file': server+'audio-only.ogg', 'width': 100 },
      { 'bitrate': 48, 'file': server+'audio-only.mp3', 'width': 100 }
/*
    'sd': [
      { 'file': server+'/Manifest' },
*/
    ],
    'download': server+'audio-only.mp3',
    'extra': {
      'src': '/static/third_party/jwplayer/player.swf'
    }
  };
}

Streams.prototype.streams = function(format) {
  if (format == 'html5') {
    return this.html5_streams;
  } else if (format == 'flash') {
    return this.flash_streams;
  } else if (format == 'audio') {
    return this.audio_streams;
  }
}

Streams.prototype.levels = function(format, quality) {
  var stream = this.streams(format);
  var levels = [];
  if (quality == 'auto') {
    levels = $.extend(true, [], stream.sd);
    if (format != 'audio') {
      levels = levels.concat($.extend(true, [], stream.hd));
    }
  } else if (quality == 'hd') {
    levels = $.extend(true, [], stream.hd);
  } else if (quality == 'sd') {
    levels = $.extend(true, [], stream.sd);
  }
  // Add the cache buster
  var cache_buster = '?q='+new Date().getTime();
  for (i in levels) {
    levels[i].file = levels[i].file + cache_buster;
  }

  return levels;
}

Streams.prototype.modes = function(format, quality) {
  var modes = [];
  var download = '';

  if (format == 'auto') {
    var modes = [];

    var html5_modes = this.modes('html5', quality);
    for (i in html5_modes) {
      if (html5_modes[i].type == 'download') {
        download = html5_modes[i].download;
        continue;
      }
      modes.push(html5_modes[i]);
    }
    var flash_modes = this.modes('flash', quality);
    for (i in flash_modes) {
      if (flash_modes[i].type == 'download') {
        continue;
      }
      modes.push(flash_modes[i]);
    }
  } else {
    var stream = this.streams(format);
    var levels = this.levels(format, quality);

    for (i in stream.modes) {
      var mode = {
        'type': stream.modes[i],
        'config': {'levels': levels}
      };
      for (key in stream.extra) {
        mode[key] = stream.extra[key];
      }
      modes.push(mode);
    }

    download = stream.download;
  }
  modes.push({
    'type': 'download',
    'config': {'file': download}
  });

  return modes;
}
