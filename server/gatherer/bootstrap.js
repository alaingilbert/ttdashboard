var postgres = require('pg');
//var sockets  = require('./sockets').sockets;
var settings = require('./settings');
var db       = require('./database_operations').DatabaseOperations;
var Process  = require('./process');
var Bot      = require('ttapi');
var flow     = require('flow');

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
   console.log(err, res);
}

// Create all bots
pg.query('SELECT * FROM bots', function (err, res) {
   flow.serialForEach(res.rows, function (row) {
      var infos  = row;
      var auth   = infos.auth;
      var userId = infos.userid;
      var roomId = infos.roomid;
      var bot    = new Bot(auth, userId, roomId);
      bot.on('roomChanged',  function (data) { Process.roomInfos  (bot, data, callback); });
      bot.on('speak',        function (data) { Process.speak      (bot, data, callback); });
      bot.on('registered',   function (data) { Process.registered (bot, data, callback); });
      bot.on('newsong',      function (data) { Process.newsong    (bot, data, callback); });
      bot.on('nosong',       function (data) { Process.nosong     (bot, data, callback); });
      bot.on('update_votes', function (data) { Process.updateVotes(bot, data, callback); });
      this();
   });
});
