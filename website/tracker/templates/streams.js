// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:
{% load safe_js %}
// Your IP is: {{yourip}}

// Server which is doing the streaming
var {{group|safe_js}}_streamer = new Streams('http://{{server|escapejs}}:8080/');
