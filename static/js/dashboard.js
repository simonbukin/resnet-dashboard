$(document).ready(function(){
  var socket = io.connect("http://" + document.domain + ":" + location.port);

  socket.on('calendar', function(msg) {
    var elem = $('#housecall');
    elem.empty();
    if(msg > 0) {
      elem.append(
      "<div class='notification is-danger'>" +
        "<h3 class='title is-3'>There " + ((msg == 1) ? "is 1" : "are " + msg) + " housecall" + ((msg > 1) ? "s today" : " today </h3>") +
      "</div>");
      // elem.text("There is " + msg + " housecall today");
    } else {
      // elem.text("Remember to clock in!");
    }
  });

  socket.on('sheets', function(msg) {
    console.log("sheets", msg);
    $("#tasks").empty();
    for(var i = 0; i < msg.length; i++) {
      $("#tasks").append("<tr><td class='is-size-5'>" + msg[i]['task'] + "</td></tr>");
    }
  });

  socket.on("wiw", function(msg) {
    console.log("wiw", msg);
    $("#wiw-rcc").empty();
    $("#wiw-stevenson").empty();
    for(var i = 0; i < msg.length; i++) {
      if(msg[i]['loc'] == 'rcc') {
        $("#wiw-rcc").append(
        "<div class='column is-narrow'>" +
          "<div class='box'>" +
            "<p class='title is-5'>" + msg[i]['name'] + "</p>" +
            // "<figure class='image is-128x128'>" +
            //   "<img class='is-rounded' src=" + msg[i]['avatar'] + ">" +
            // "</figure>" +
          "</div>" +
        "</div>");
      } else {
        $("#wiw-stevenson").append(
        "<div class='column is-narrow'>" +
          "<div class='box'>" +
            "<p class='title is-5'>" + msg[i]['name'] + "</p>" +
            // "<figure class='image is-128x128'>" +
            //   "<img class='is-rounded' src=" + msg[i]['avatar'] + ">" +
            // "</figure>" +
          "</div>" +
        "</div>");
      }
    }
  });
});
