var postgres = require('pg');
//var sockets  = require('./sockets').sockets;
var settings = require('./settings');
var db       = require('./database_operations').DatabaseOperations;
var Process  = require('./process');
var Bot      = require('ttapi');

var pg = new postgres.Client({
   user:     settings.POSTGRES_USER,
   password: settings.POSTGRES_PASW,
   database: settings.POSTGRES_DB
});

pg.connect();

db.setDatabase(pg);
Process.db = db;

// Start the socket server
//sockets.setDb(db);
//sockets.listen(9000);

function callback(err, res) {
   if (err) { console.log(err); }
}

// Create all bots
var query = pg.query('SELECT * FROM bots');

query.on('row', function (row) {
   var auth   = row.auth;
   var userId = row.userid;
   var roomId = row.roomid;
   var bot    = new Bot(auth, userId, roomId);
   bot.name   = userId;
   bot.debug  = false;
   bot.on('roomChanged',  function (data) { Process.roomInfos  (bot, data, function () {
      bot.on('speak',        function (data) { Process.speak      (bot, data, callback); });
      bot.on('registered',   function (data) { Process.registered (bot, data, callback); });
      bot.on('newsong',      function (data) { Process.newsong    (bot, data, callback); });
      bot.on('nosong',       function (data) { Process.nosong     (bot, data, callback); });
      bot.on('update_votes', function (data) { Process.updateVotes(bot, data, callback); });
      console.log('Bot started. ('+bot.name+')');
   }); });
});
