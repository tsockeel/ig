var addMessage = function(msg) {
    var newMsg = $('<a/>');
    newMsg.addClass("thumbnail");
    newMsg.addClass("href", msg.message);
    var im = $('<img>');
    im.attr('src', msg.message);
    im.attr('alt', '...');
    im.appendTo(newMsg);
    newMsg.prependTo('#live');
  }


 $(document).ready(function() {

    var socket = io.connect('http://66.228.61.74:3000');

    socket.on('notification', function(data) {
      console.log('Notification received: ' + data.message);
      addMessage(data);
    });

    socket.on('connect', function() {
       console.log('Connected ');
    });

  });
