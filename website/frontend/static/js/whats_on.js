// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

var time_local = Date.now();
function current_time() {
  return Date.now() - 18000*1e3;
}

var schedule = [];
function get_schedule(callback) {
  $.ajax({
    url: '/schedule.js',
    dataType: 'json',
    cache: true,
    async: true,
    success: function(data) {
      schedule = data;
      callback();
    }
  });
}

function current_session(group) {
  var time = current_time();

  for (var i = 0; i < schedule.length; i++) {
    var talk = schedule[i];
    if (group)
      if (!talk['room'] || talk['room'] != group) {
        continue;
      }

    var start = Date.parse(talk['start_iso'] + "Z");
    var duration = parseInt(talk['duration'])*60;
    var end = start + duration*1e3;

    if (time >= start && time < end) {
      return talk;
    }
  }
}

function update_schedule(widget_title, widget_desc, group) {
  var talk = current_session(group);

  if (!talk) {
    talk = current_session();
  }

  if (!talk) {
    talk = new Array();
    talk['title'] = "Unknown Talk";
    talk['description'] = 'Cannot get talk title and description.';
  }

  var title = "";
  if (talk['url']) {
    title += "<a href='" + talk['url'] + "' onClick=\"return confirm('Leave the video?');\">";
  }
  title += talk['title'];
  if (talk['url']) {
    title += "</a>";
  }
  widget_title.html(title);

  widget_desc.html("<br>" + talk['description'].replace("\n", '<br><br>'));
}
