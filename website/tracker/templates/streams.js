{% comment %}
-*- coding: utf-8 -*-
vim: set ts=2 sw=2 et sts=2 ai ft=htmldjango:
{% endcomment %}{% load safe_js %}
var streamers_active = new Array();
{% for server in active_servers %}streamers_active.push("{{server.group|escapejs}}");{% if DEBUG %} // {{server.ip}} - Last seen at {{server.lastseen}}{% endif %}
{% endfor %}
