var timer = setInterval(timing_loop, 1000);

function timing_loop() {
  $.getJSON($SCRIPT_ROOT + '/_loop', {
    // for arg values
  }, function(data) {
    $("#test").empty()
    for(var i = 0; i < data.length; i++) {
      $("#test").append("<li>" + data[i].name + "</li>");
    }
  });
}
