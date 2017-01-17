// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

function current_time() {
  return Date.now() - 18000*1e3;
}

var schedule = [], schedules = [];
var interval = function(){
  $('.now_time').each(function(ind, ele){
    var raw = $(ele).attr('rawend');

    var endTime = moment(raw);
    var diff = moment.duration(endTime.diff(moment()));

    var str = "ends in ";

    if(diff.days() > 1) str = str + Math.floor(diff.days()) + "d "
    if(diff.hours() > 1) str = str + Math.floor(diff.hours()) + "h "
    if(diff.minutes() > 1) str = str + Math.floor(diff.minutes()) + "m "
    if(diff.seconds() > 1) str = str + Math.floor(diff.seconds()) + "s"

    $(ele).html(str);
  });
}

setInterval(interval, 60e3);
setTimeout(interval, 2e3);
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

function update_schedule(widget_title, widget_desc, group, next_title, next_desc, next_time, now_time, group_key, now_url, next_url) {
  var talk = schedule;
  if(group_key) talk = schedules[group_key];
  var url = null, generated = false;

  var title = "", description = "";
  if (talk && talk.length) {
    title = talk[0]['title'];
    if(talk[0]['url']) {
        url = talk[0]['url'];
    }
    if(talk[0]['abstract']) description = talk[0]['abstract'];
    if(talk[0]['generated']) {
      generated = true;
    }
    if (now_time && talk[0]['start']) {
      now_time.attr('rawstart', talk[0].start);
    }
    if (now_time && talk[0]['end']) {
      now_time.attr('rawend', talk[0].end);
    }
  } else {
    title = "Unknown Talk";
    description = 'Cannot get talk title and description.';
  }

  widget_title.text(title);
  if (widget_desc) {
    widget_desc.html(description);
  }
  if (now_url) {
    if (!url) {
      now_url.hide();
    } else {
      now_url.show();
      now_url.attr('href', url);
    }
  }
  if (generated) {
    widget_title.addClass('event-generated');
  } else {
    widget_title.removeClass('event-generated');
  }

  title = "";
  description = "";
  url = null;
  generated = false;

  if (talk && talk.length > 1 && next_title) {
    if(talk[1] && talk[1]['title']) {
      title = talk[1]['title'];
      if(talk[1]['url']){
        url = talk[1]['url'];
      }
      if(talk[1]['abstract']) description = talk[1]['abstract'];
      if(talk[1]['generated']) {
        generated = true;
      }
    }
    next_title.text(title);
    if (next_desc) {
      next_desc.html(description);
    }
    if(next_time) {
      var next_talk_start = moment(talk[1].start);
      next_talk_start.local();
      if (next_talk_start.isSame(moment(), 'day')) {
        next_time.text('starts at ' + next_talk_start.format('HH:mm'));
      } else {
        next_time.text('starts at ' + next_talk_start.format('llll'));
      }
      next_time.attr('rawstart', talk[1].start);
      next_time.attr('rawend', talk[1].end);
    }
    if (next_url) {
      if (!url) {
        next_url.hide();
      } else {
        next_url.show();
        next_url.attr('href', url);
      }
    }
    if (generated) {
      next_title.addClass('event-generated');
    } else {
      next_title.removeClass('event-generated');
    }
  }
}
