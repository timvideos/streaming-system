function sendreport() {
  format = $('input[name="format"]:checked').val();
  quality = $('input[name="quality"]:checked').val();
  path = window.location.pathname;
  window.location.href = 'http://bugtracker.timvideos.us' + '/bugform/?format=' + format + '&quality=' + quality + '&path=' + path; 
}
