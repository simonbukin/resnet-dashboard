var timer = setInterval(timing_loop, 200);

function timing_loop() {
  $.getJSON($SCRIPT_ROOT + '/_loop', {
    // for arg values
  }, function(data) {
    $("#result").text(data.result);
  });
}
