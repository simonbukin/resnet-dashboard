var timer = setInterval(timing_loop, 1000);

function timing_loop() {
  $.getJSON($SCRIPT_ROOT + '/_loop', {
    // for arg values
  }, function(data) {
    $("#tasks").empty()
    $("#shifts").empty()
    for(var i = 0; i < data['wiw'].length; i++) {
      $("#shifts").append("<li>" + data['wiw'][i]['name'] + "</li>");
    }
    for(var i = 0; i < data['sheets'].length; i++) {
      $("#tasks").append("<tr><td>" +
      data['sheets'][i]['task'] + "</td> <td>" +
      data['sheets'][i]['description'] + "</td> <td>" +
      data['sheets'][i]['techs'] + "</td> <td>" +
      data['sheets'][i]['status'] + "</td> <td>" +
      data['sheets'][i]['created'] + "</td> <td>" +
      data['sheets'][i]['finished'] + "</td> <td>" +
      data['sheets'][i]['due']
      + "</tr>");
    }
  });
}
