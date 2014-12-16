var app = require('express')();
var server = require('http').Server(app);
var redis = require('redis');
var io = require('socket.io')(server);

server.listen(3000);
// Create redis client
client = redis.createClient(6379, '127.0.0.1', {});

// Subscribe to the Redis events channel
client.subscribe('message');

io.on('connection', function (socket) {

	console.log('New connection ');

	// Grab message from Redis and send to client
	client.on('message', function(channel, data){
		console.log('on message', data);
		// Re-send message to the browser using Socket.IO
		socket.emit('notification', { message : data });
	});
});
