// initialization
$(document).ready(function() {
  // connect to Flask socket
  var socket = io.connect("http://" + document.domain + ":" + location.port);

  // when calendar event sent
  socket.on('calendar', function(msg) {
    ;
  });

  // update water day display
  socket.on('water', function(msg) {
    ;
  })

  // when sheet event sent
  socket.on('sheets', function(msg) {
    // console.log("sheets", msg);
    ;
  });

  socket.on('trello', function(msg) {
    ;
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
