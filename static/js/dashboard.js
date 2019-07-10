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
    } else {
      elem.append("<p class='is-size-3'>Remember to clock in!</p>");
    }
  });

  socket.on('sheets', function(msg) {
    console.log("sheets", msg);
    $("#tasks").empty();
    for(var i = 0; i < msg.length; i++) {
      $("#tasks").append("<tr><td class='is-size-3'>" + msg[i]['task'] + "</td></tr>");
    }
  });

  socket.on('itr', function(msg) {
    // console.log("itr", msg);
    $('#tickets').empty();
    var tickets = msg['tickets'];
    console.log(tickets);
    console.log(tickets.length);
    for(var i = 0; i < tickets.length; i++) {
      console.log(tickets[i]);
    }
    for(var i = 0; i < tickets.length; i++) {
      if(tickets[i]['priority'] == 1) {
        $('#tickets').append("<tr><td class='is-size-3 has-background-danger'>" + tickets[i]['ticket_name'] + "</td></tr>");
      } else if(tickets[i]['priority'] == 0) {
        $('#tickets').append("<tr><td class='is-size-3 has-background-warning'>" + tickets[i]['ticket_name'] + "</td></tr>");
      } else {
        $('#tickets').append("<tr><td class='is-size-3'>" + tickets[i]['ticket_name'] + "</td></tr>");
      }
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
            "<p class='title is-4'>" + msg[i]['name'] + "</p>" +
          "</div>" +
        "</div>");
      } else {
        $("#wiw-stevenson").append(
        "<div class='column is-narrow'>" +
          "<div class='box'>" +
            "<p class='title is-4'>" + msg[i]['name'] + "</p>" +
          "</div>" +
        "</div>");
      }
    }
  });
});
