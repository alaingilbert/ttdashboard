var fs       = require('fs');
var nodeunit = require('nodeunit');
var postgres = require('pg');
var settings = require('../settings');
var db       = require('../database_operations').DatabaseOperations;

var pg = new postgres.Client({
   user:     settings.POSTGRES_USER,
   password: settings.POSTGRES_PASW,
   database: settings.POSTGRES_DB
});


function truncTables(callback) {
   var sql = 'TRUNCATE users,                            ' +
             '         songs,                            ' +
             '         rooms,                            ' +
             '         chat_log,                         ' +
             '         song_log,                         ' +
             '         users_songs_liked RESTART IDENTITY';
  pg.query(sql, function (err, res) {
    callback();
  });
}


exports.initDb = function (test) {
  pg.connect();
  pg.query('DROP DATABASE IF EXISTS ttdashboard_unit_tests', function (err, res) {
  pg.query('CREATE DATABASE ttdashboard_unit_tests', function (err, res) {
    pg.end();

    // Connect on the new database
    pg = new postgres.Client({
      user:     settings.POSTGRES_USER,
      password: settings.POSTGRES_PASW,
      database: 'ttdashboard_unit_tests'
    });
    pg.connect();
    db.setDatabase(pg);

    // Create the schemas
    fs.readFile('../schemas.sql', function (err, data) {
      var buf = data.toString('binary');
      pg.query(buf, function (err, res) {
        if (err) { console.log(err); process.exit(); }
        test.done();
      });
    });
  });
  });
};


exports['rooms'] = nodeunit.testCase({
   setUp: function (cb) {
      var self = this;
      cb();
   },


   tearDown: function (cb) {
      // Empty all tables
      truncTables(function () {
         cb();
      });
   },


   'room.createUpdate': function (test) {
      test.expect();


      var roomid               = '4e0e243799968e514e00032c'
        , name                 = 'room1'
        , created              = new Date()
        , description          = null
        , shortcut             = null
        , currentDjId          = null
        , currentDjName        = null
        , listeners            = 100
        , upvotes              = 5
        , downvotes            = 10
        , currentSongId        = null
        , currentSongName      = null
        , currentSongStarttime = null;

      // Create a new room
      db['room.createUpdate'](roomid, name, created, description, shortcut, currentDjId,
                              currentDjName, listeners, upvotes, downvotes, currentSongId,
                              currentSongName, currentSongStarttime, function (err, room1) {
      test.equal(typeof room1.id, 'number');
      test.equal(room1.roomid, roomid);
      test.equal(room1.name, name);
      test.notStrictEqual(room1.created, null);
      test.equal(room1.listeners, 100);
      test.equal(room1.upvotes, 5);
      test.equal(room1.downvotes, 10);

      // Update an existing room
      listeners = 101;
      upvotes   = 20;
      downvotes = 30;
      db['room.createUpdate'](roomid, name, created, description, shortcut, currentDjId,
                              currentDjName, listeners, upvotes, downvotes, currentSongId,
                              currentSongName, currentSongStarttime, function (err, room2) {
      test.equal(typeof room2.id, 'number');
      test.equal(room2.roomid, room1.roomid);
      test.equal(room2.name, name);
      test.notStrictEqual(room2.created, null);
      test.equal(room2.listeners, 101);
      test.equal(room2.upvotes, 20);
      test.equal(room2.downvotes, 30);


      test.done();
      });
      });
   },


   'room.update': function (test) {
      var self = this;
      test.expect();

      db['room.update']({ id: 2, song: 'CALISS' }, function (err, res) {

         console.log(err, res);

         test.done();
      });
   }
});


exports.dropDb = function (test) {
  // Drop the unit tests database
  pg.end();
  pg = new postgres.Client({
    user:     settings.POSTGRES_USER,
    password: settings.POSTGRES_PASW,
    database: 'postgres'
  });
  pg.connect();
  pg.query('DROP DATABASE ttdashboard_unit_tests', function (err, res) {
    if (err) { console.log(err); process.exit(); }
    pg.end();
    test.done();
  });
};
