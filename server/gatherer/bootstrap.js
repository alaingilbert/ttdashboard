var postgres = require('pg');
var sockets  = require('./sockets').sockets;
var settings = require('./settings');
var db       = require('./database_operations').DatabaseOperations;

var pg = new postgres.Client({
   user:     settings.POSTGRES_USER,
   password: settings.POSTGRES_PASW,
   database: settings.POSTGRES_DB
});

pg.connect();

db.setDatabase(pg);
sockets.setDb(db);
sockets.listen(9000);
