// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

// Server which is doing the streaming
var {{group}}_streamer='http://{{server|escapejs}}:8080/';

var {{group}}_html5_streams = {
  'modes': ['html5'],
  'hd': [
    { 'file': {{group}}_streamer+'webcast-high.webm' },
  ],
  'sd': [
    { 'file': {{group}}_streamer+'webcast-low.webm' },
  ],
  'download': {{group}}_streamer+'webcast-low.webm'
};

var {{group}}_flash_streams = {
  'modes': ['flash'],
  'hd': [
    { 'bitrate': 800, 'file': {{group}}_streamer+'webcast-high.flv', 'width': 720 }
  ],
  'sd': [
    { 'bitrate': 300, 'file': {{group}}_streamer+'webcast-low.flv', 'width': 432 }
  ],
  'download': {{group}}_streamer+'webcast-low.ogv',
  'extra': {
    'src': '/static/third_party/jwplayer/player.swf'
  }
};

var {{group}}_audio_streams = {
  'modes': ['html5', 'flash'],
  'sd': [
    { 'bitrate': 192, 'file': {{group}}_streamer+'audio-only.aac', 'width': 100 },
    { 'bitrate': 128, 'file': {{group}}_streamer+'audio-only.ogg', 'width': 100 },
    { 'bitrate': 48, 'file': {{group}}_streamer+'audio-only.mp3', 'width': 100 }
  ],
  'download': {{group}}_streamer+'audio-only.mp3',
  'extra': {
    'src': '/static/third_party/jwplayer/player.swf'
  }
};

function {{group}}_jwplayer_streams(format) {
  if (format == 'html5') {
    return {{group}}_html5_streams;
  } else if (format == 'flash') {
    return {{group}}_flash_streams;
  } else if (format == 'audio') {
    return {{group}}_audio_streams;
  }
}

function {{group}}_jwplayer_levels(format, quality) {
  var stream = {{group}}_jwplayer_streams(format);
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

function {{group}}_jwplayer_modes(format, quality) {
  var modes = [];
  var download = '';

  if (format == 'auto') {
    var modes = [];

    var html5_modes = {{group}}_jwplayer_modes('html5', quality);
    for (i in html5_modes) {
      if (html5_modes[i].type == 'download') {
        download = html5_modes[i].download;
        continue;
      }
      modes.push(html5_modes[i]);
    }
    var flash_modes = {{group}}_jwplayer_modes('flash', quality);
    for (i in flash_modes) {
      if (flash_modes[i].type == 'download') {
        continue;
      }
      modes.push(flash_modes[i]);
    }
  } else {
    var stream = {{group}}_jwplayer_streams(format);
    var levels = {{group}}_jwplayer_levels(format, quality);

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
