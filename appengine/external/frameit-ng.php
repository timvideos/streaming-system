<?php
// -*- coding: utf-8 -*-
// vim: set ts=2 sw=2 et sts=2 ai:

$channel = $_GET['channel'];

$contents = file_get_contents("/var/cache/ircd/public_html/{$channel}/latest.log.html");
$start = strpos($contents, '<tr ');
$end = strpos($contents, '</table>');

$rows = preg_split('/<\/tr>/', substr($contents, $start, $end-$start));
$rrows = array_reverse($rows);

?>
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <link rel="stylesheet" href="http://extra.streamti.me/~irc/<?php echo urlencode($channel); ?>/irclog.css" />
<style>
* {
  font-size: 9pt;
}

.part, .join, .servermsg, .nickchange, .other, .time { font-size: 7pt; }

</style>
 </head>
<body>
<table class="irclog">
<?
foreach($rrows as $line) {
 echo $line . "</tr>";
}
?>
</table>
</body>
</html>
