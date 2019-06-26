var timer = setInterval(timing_loop, 2000);

function timing_loop() {
  $.getJSON($SCRIPT_ROOT + '/_loop', {
    // for arg values
  }, function(data) {
    $("#tasks").empty()
    $("#shifts-rcc").empty()
    $("#shifts-stevenson").empty()
    for(var i = 0; i < data['wiw-rcc'].length; i++) {
      $("#shifts-rcc").append("<div class='column is-narrow'>" +
                                "<div class='box'>" +
                                  "<p class='title'>" + data['wiw-rcc'][i]['name'] + "</p>" +
                                  "<figure class='image is-128x128'>" +
                                    "<img class='is-rounded' src=" + data['wiw-rcc'][i]['avatar'] + ">" +
                                  "</figure>" +
                                "</div>" +
                              "</div>");
    }
    for(var i = 0; i < data['wiw-stevenson'].length; i++) {
      $("#shifts-stevenson").append("<div class='column is-narrow'>" +
                                      "<div class='box'>" +
                                        "<p class='title'>" + data['wiw-stevenson'][i]['name'] + "</p>" +
                                        "<figure class='image is-128x128'>" +
                                          "<img class='is-rounded' src=" + data['wiw-stevenson'][i]['avatar'] + ">" +
                                        "</figure>" +
                                      "</div>" +
                                    "</div>");
    }
    for(var i = 0; i < data['sheets'].length; i++) {
      $("#tasks").append("<tr><td class='is-size-5'>" + data['sheets'][i]['task'] + "</td></tr>");
    }
  });
}
