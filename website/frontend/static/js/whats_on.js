// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

var time_local = Date.now();
function current_time() {
  return Date.now() - 18000*1e3;
}

var schedule = [], schedules = [];
function get_schedule(callback, group) {
  $.ajax({
    url: '/' + group + '/json',
    dataType: 'json',
    cache: true,
    async: true,
    success: function(data) {
      if(group) schedules[group] = data;
      else schedule = data;
      callback();
    }
  });
}

function update_schedule(widget_title, widget_desc, group, next_title, next_desc, next_time, group_key) {
  var talk = schedule;
  if(group_key) talk = schedules[group_key];

  var title = "", description = "";
  if (talk && talk.length) {
    title = talk[0]['title'];
    if(talk[0]['url']){
      title = '<a href="' + talk[0]['url'] + ' "onClick="return confirm(\'Leave the video?\');">' + title + '</a>';
    }
    if(talk[0]['abstract']) description = talk[0]['abstract'];
  } else {
    title = "Unknown Talk";
    description = 'Cannot get talk title and description.';
  }

  widget_title.html(title);
  widget_desc.html("<br>" + description.replace("\n", '<br><br>'));

  title = "";
  description = "";

  if (talk && talk.length > 1 && next_title) {
    if(talk[1] && talk[1]['title']) {
      title = talk[1]['title'];
      if(talk[1]['url']){
        title = '<a href="' + talk[1]['url'] + ' "onClick="return confirm(\'Leave the video?\');">' + title + '</a>';
      }
      if(talk[1]['abstract']) description = talk[1]['abstract'];
    }
    next_title.html(title);
    if(next_desc) next_desc.html("<br>" + description.replace("\n", '<br><br>'));
    if(next_time) next_time.html(talk[1].start.substring(11, 16));
  }
}
