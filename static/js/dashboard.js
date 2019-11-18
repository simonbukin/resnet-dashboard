// initialization
$(document).ready(function() {
  // connect to Flask socket
  var socket = io.connect("http://" + document.domain + ":" + location.port);

  // when calendar event sent
  socket.on('calendar', function(msg) {
    var elem = $('#housecall');
    elem.empty(); // get and empty housecall div
    if(msg > 0) { // at least 1 housecall
      elem.append( // add notification for X housecall(s)
      "<div class='notification is-danger'>" +
        "<h3 class='title is-3'>There " + ((msg == 1) ? "is 1" : "are " + msg) + " housecall" + ((msg > 1) ? "s today" : " today </h3>") +
      "</div>");
    } else { // otherwise add message of the day
      elem.append("<p class='is-size-3'>Remember to clock in!</p>");
    }
  });

  // update water day display
  socket.on('water', function(msg) {
    var elem = $('#water');
    elem.empty();
    if (msg === 1) {
      elem.append(
        "<div class='notification is-info'>" + 
          "<h3 class='title is-3'>It is water day</h3>" + 
        "</div>"
      );
    }
  })

  // when sheet event sent
  socket.on('sheets', function(msg) {
    // console.log("sheets", msg);
    $("#tasks").empty(); // empty tasks div
    for(var i = 0; i < msg.length; i++) { // add each task title as a table row
      $("#tasks").append("<tr><td class='is-size-3'>" + msg[i]['title'] + "</td></tr>");
    }
  });

  socket.on('trello', function(msg) {
    $("#tasks").empty(); // empty tasks div
    for(var i = 0; i < msg.length; i++) { // add each task title as a table row
      $('#tasks').append("<tr><td class='is-size-3'>" + msg[i] + "</td></tr>");
    }
  });

  // when itr event sent
  socket.on('itr', function(msg) {
    // console.log("itr", msg);
    $('#tickets').empty(); // empty tickets div
    var tickets = msg['tickets'];
    for(var i = 0; i < tickets.length; i++) {
      if(tickets[i]['priority'] == 0) { // add ticket to table based on priority
        $('#tickets').append("<tr><td class='is-size-3 has-background-danger'>" + tickets[i]['ticket_name'] + "</td></tr>");
      } else if(tickets[i]['priority'] == 1) {
        $('#tickets').append("<tr><td class='is-size-3 has-background-warning'>" + tickets[i]['ticket_name'] + "</td></tr>");
      } else if(tickets[i]['priority'] == 2) {
        $('#tickets').append("<tr><td class='is-size-3 has-background-info'>" + tickets[i]['ticket_name'] + "</td></tr>");
      } else {
        $('#tickets').append("<tr><td class='is-size-3'>" + tickets[i]['ticket_name'] + "</td></tr>");
      }
    }
  });
});
