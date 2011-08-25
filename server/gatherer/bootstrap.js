var mongo   = require('mongodb');
var sockets = require('./sockets').sockets;

sockets.setDb(mongo);
sockets.listen(8000);
