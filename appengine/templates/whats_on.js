// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

var time_local = Date.now();
var time_server = {{current_time}}*1000;
function current_time() {
  return Date.now() - (time_local-time_server);
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
      if (!talk['Room Name'] || talk['Room Name'].toLowerCase() != group) {
        continue;
      }

    var start = Date.parse(talk['Start'] += " GMT") - 39600000;
    var duration_bits = talk['Duration'].split(':');
    var duration = parseInt(duration_bits[0])*60*60 + parseInt(duration_bits[1])*60 + parseInt(duration_bits[2]);
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
    talk['Title'] = "Unknown Talk";
    talk['Description'] = 'Cannot get talk title and description.';
  }

  var title = "";
  if (talk['URL']) {
    title += "<a href='" + talk['URL'] + "' onClick=\"return confirm('Leave the video?');\">";
  }
  title += talk['Title'];
  if (talk['URL']) {
    title += "</a>";
  }
  widget_title.html(title);

  widget_desc.html("<br>" + talk['Description'].replace("\n", '<br><br>'));
}
