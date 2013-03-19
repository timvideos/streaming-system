// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

/*

jwplayer("myElement").setup({
    playlist: [{
        image: "/assets/sintel.jpg",
        sources: [
            { file: "/assets/sintel.mp4", label: "360p" },
            { file: "/assets/sintel-hd.mp4", label: "720p HD" }
        ],
        title: "Sintel Movie Trailer"
    }]
});

var settings = {
 image: "",
 title: "",
};

 */

// Details
// ----------------------------------------------------------
// The MP4 format, with H264 video and AAC audio.
// The WebM format, with VP8 video and Vorbis audio.
// The FLV format, with H263 video and MP3 audio.
// ----------------------------------------------------------
//   sd:  640*480 - 4:3 -  300e3 bit/sec
//   hd:  792*576 - 4:3 -  800e3 bit/sec
// dual: 1584*576 - 8:3 - 1400e3 kbit/sec


function Streams (server) {
    this.server = server;
}

Streams.prototype.settings = function (type) {
  var settings = {};

  switch(type) {
  
  // Auto selection between HTML5 formats and Flash
  case "auto":
    settings = {
      playlist: [{
        sources: [
          // HTML5: Chrome, Firefox, Opera
          { file: this.server+"webcast-high.webm",  label: "HTML5 HD", height: 576, width:  792 },
          { file: this.server+"webcast-low.webm",   label: "HTML5 SD", height: 480, width:  640 },
          // { file: this.server+"webcast-dual.webm", label: "HTML5 Dual", height: 576, width: 1584 },
          // HTML5: Safari, IE9
          { file: this.server+"webcast-high.mp4",   label: "HTML5 HD", height: 576, width:  792 },
          { file: this.server+"webcast-low.mp4",    label: "HTML5 SD", height: 480, width:  640 },
          // { file: this.server+"webcast-dual.mp4", label: "HTML5 Dual", height: 576, width: 1584 },

          // Flash fallback
          // { file: this.server+"????????????.smil", label: "Flash Auto" }, // Adaptive RTMP Streaming on Amazon cloudfront
          { file: this.server+"webcast-high.flv",   label: "Flash HD", height: 576, width:  792 },
          { file: this.server+"webcast-low.flv",    label: "Flash SD", height: 480, width:  640 }
        ]
      }],
      primary: 'html5',
      fallback: 'flash'
    };
    break;

  // Flash only fallback
  case "flash":
    settings = {
      playlist: [{
        sources: [
          // { file: this.server+"????????????.smil", label: "Flash Auto"}, // RTMP Streaming on Amazon cloudfront
          { file: this.server+"webcast-high.flv",   label: "Flash HD", height: 576, width:  792 },
          { file: this.server+"webcast-low.flv",    label: "Flash SD", height: 480, width:  640 }
        ]
      }],
      primary: 'flash',
      fallback: 'flash'
    };
    break;
 
  // Mobile for Android/iPhone/iPad
  case "mobile":
    settings = {
      playlist: [{
        sources: [
          { file: this.server+"webcast.m3u8" },     // HLS Streaming for iPhone/iPad
          { file: this.server+"webcast-mobile.mp4"} // Default Android Mobile Fallback
        ]
      }],
      primary: 'html5',
      fallback: 'download'
    };
    break;

  //  Audio fallback
  case "audio":
    settings = { 
      playlist: [{
        sources: [
          { file: this.server+"webcast.mp3" },
          { file: this.server+"webcast.ogg" },
          { file: this.server+"webcast.aac" }
        ]
      }],
      primary: 'html5',
      fallback: 'download'
    };
    break;

  default:
    if (window.console)
      console.log('Unknown type');
    return {};
  }

  // Add the cache buster
  var cache_buster = '?q='+new Date().getTime();
  for (source in settings.playlist[0].sources) {
    source.file = source.file + '?' + cache_buster;
  }

  return settings;
};
