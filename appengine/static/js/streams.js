// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

// Server which is doing the streaming
var streamer='http://49.156.19.78:8080/';

var html5_streams = {
  'modes': ['html5'],
  'hd': [
    { 'file': streamer+'webcast-high.webm' },
	  { 'file': streamer+'webcast-high.ogv' },
	  //{ file: streamer+'webcast-high.mp4' }
  ],
  'sd': [
    { 'file': streamer+'webcast-low.webm' },
    { 'file': streamer+'webcast-low.ogv' },
  ],
  'download': streamer+'webcast-low.ogv'
};

var flash_streams = {
  'modes': ['flash'],
  'hd': [
    { 'bitrate': 800, 'file': streamer+'webcast-high.flv', 'width': 720 }
  ],
  'sd': [
    { 'bitrate': 300, 'file': streamer+'webcast-low.flv', 'width': 432 }
  ],
  'download': streamer+'webcast-low.ogv',
  'extra': {
    'src': '/static/third_party/jwplayer/player.swf'
  }
};

var audio_streams = {
  'modes': ['flash', 'html5'],
  'sd': [
    { 'bitrate': 192, 'file': streamer+'audio-only.aac' },
    { 'bitrate': 128, 'file': streamer+'audio-only.ogg' },
    { 'bitrate': 48, 'file': streamer+'audio-only.mp3' }
  ],
  'download': streamer+'audio-only.mp3',
  'extra': {
    'src': '/static/third_party/jwplayer/player.swf'
  }
};

function jwplayer_streams(format) {
  if (format == 'html5') {
    return html5_streams;
  } else if (format == 'flash') {
    return flash_streams;
  } else if (format == 'audio') {
    return audio_streams;
  }
}

function jwplayer_levels(format, quality) {
  var stream = jwplayer_streams(format);
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
  var cache_buster = '?'+new Date().getTime();
  for (i in levels) {
    levels[i].file = levels[i].file + cache_buster;
  }

  return levels;
}

function jwplayer_modes(format, quality) {
  var modes = [];
  var download = '';

  if (format == 'auto') {
    var modes = [];

    var html5_modes = jwplayer_modes('html5', quality);
    for (i in html5_modes) {
      if (html5_modes[i].type == 'download') {
        download = html5_modes[i].download;      
        continue;
      }
      modes.push(html5_modes[i]);
    }
    var flash_modes = jwplayer_modes('flash', quality);
    for (i in flash_modes) {
      if (flash_modes[i].type == 'download') {
        continue;
      }
      modes.push(flash_modes[i]);
    }
  } else {
    var stream = jwplayer_streams(format);
    var levels = jwplayer_levels(format, quality);

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
