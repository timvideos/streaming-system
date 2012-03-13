{% comment %}
-*- coding: utf-8 -*-
vim: set ts=2 sw=2 et sts=2 ai ft=htmldjango:
{% endcomment %}{% load safe_js %}
{%if DEBUG %}// Your server has - Active {{your_server.overall_clients}} clients @ {{your_server.overall_bitrate}} bit/s{% endif %}
var streamer_{{group|safe_js}} = {% if not your_server %}null; // No active servers found :({% else %}new Streams('http://{{your_server.ip|escapejs}}:8080/');{% endif %}

{% if DEBUG %}{% for server in active_servers %}// {{server.ip}} - Active {{server.overall_clients}} clients @ {{server.overall_bitrate}} bit/s{% endfor %}{% endif %}
