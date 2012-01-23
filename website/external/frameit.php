<?php
// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:
?>
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.5.2/jquery.min.js"></script>
    <style type="text/css">
      .a {
        width: 100%;
        height: 100%;
        border:0;
        margin:0;
        padding:0;
        overflow: hidden;
      }
      .b {
        position:absolute;
        bottom:0;
      }
    </style>
    <script type="text/javascript">
      function update() {
        $('.navigation', window.frames[0].document).hide();
        $('.generatedby', window.frames[0].document).hide();
        $('h1', window.frames[0].document).hide();
        $('.searchbox', window.frames[0].document).hide();

        $('.irclog', window.frames[0].document).resize(bump);
        bump();
        setTimeout(bump, 50);
      }
      function bump() {
        $('#wrapper').css('height', $('body', window.frames[0].document).height()+20+'px');
      }
      function wait_frame() {
        if ($('.irclog', window.frames[0].document).length == 0) {
          setTimeout(wait_frame, 50);
        } else {
         update();
         $(window).resize(update);
        }
      }

      $(document).ready(wait_frame);
    </script>
  </head>
  <body class="a">
    <div id=wrapper class="a b">
      <iframe id=frame class="a" src="/~irc/<?php echo urlencode($_GET['channel']); ?>/latest.log.html"></iframe>
    </div>
  </body>
</html>
