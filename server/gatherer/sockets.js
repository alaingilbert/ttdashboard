Object.defineProperty(Object.prototype, "$update", {
    enumerable: false,
    value: function(from) {
        var props = Object.getOwnPropertyNames(from);
        var dest = this;
        props.forEach(function(name) {
            if (name in dest) {
                var destination = Object.getOwnPropertyDescriptor(from, name);
                Object.defineProperty(dest, name, destination);
            }
        });
        return this;
    }
});

Object.defineProperty(Object.prototype, '$get', {
   value: function (name, def) {
      if (def === undefined) { def = null; }
      return this[name] !== undefined ? this[name] : def;
   }
});


var sockets = {
   db: null,
   setDb: function (db) { this.db = db; },


   listen: function (port) {
      var self = this;
      this.io = require('socket.io').listen(port);
      this.io.sockets.on('connection', function (socket) { self.setSocket(socket); });
   },


   setSocket: function (socket) {
      var self = this;


      socket.set('isAuth', false);


      /**
       * Authenticate a data provider (an extension)
       * @sig apiKey:string, callback:fn -> succeed:bool
       */
      socket.on('auth', function (data, callback) {
         if (typeof callback !== 'function')    { socket.disconnect(); return false; }
         if (!data || typeof data !== 'object') { socket.disconnect(); return callback('Invalid data', null); }

         var apiKey = data.apiKey;

         if (typeof apiKey !== 'string' || apiKey.length !== 40) {
            return callback('auth - Invalid api key', null);
         }

         // TODO: Implement the authentification
         // If provider is banned, close the socket.
         socket.set('isAuth', true, function () {
            callback(null, true);
         });
      });


      /**
       * Receive the data from a provider.
       * @sig data:obj, callback:fn -> succeed:bool
       */
      socket.on('data', function (data, callback) {
         if (typeof callback !== 'function')    { socket.disconnect(); return false; }
         if (!data || typeof data !== 'object') { socket.disconnect(); return callback('Invalid data', null); }

         socket.get('isAuth', function (err, isAuth) { if (isAuth) {
            var command = data.$get('command');
            if (command) {
               switch (command) {
                  case 'registered':
                     self.processRegistered(socket, data, callback);
                     break
                  case 'deregistered':
                     self.processDeregistered(socket, data, callback);
                     break
                  case 'newsong':
                     self.processNewsong(socket, data, callback);
                     break
                  case 'booted_user':
                     callback(null, true);
                     break
                  case 'add_dj':
                     callback(null, true);
                     break
                  case 'rem_dj':
                     callback(null, true);
                     break
                  case 'new_moderator':
                     callback(null, true);
                     break
                  case 'update_votes':
                     self.processUpdateVotes(socket, data, callback)
                     break;
                  case 'speak':
                     self.processSpeak(socket, data, callback);
                     break;
                  default:
                     callback(null, true);
                     break;
               }
            } else {
               var msgid = data.$get('msgid');
               var room  = data.$get('room');

               // The guy register in a room
               if (msgid && room) {
                  self.processRoomInfos(socket, data, callback)
               } else {
                  var rooms = data.$get('rooms');

                  // The guy is on the main page (not in a room)
                  if (msgid && rooms) {
                     self.processRooms(socket, data, callback);
                  } else {

                     // We don't know this packet
                     callback(null, true);
                  }
               }
            }
         } else { callback('Not authenticated', null); socket.disconnect(); } });
      });


      socket.on('disconnect', function () {
      });
   },


   processRegistered: function (socket, data, callback) {
      callback(null, true);
   },


   processDeregistered: function (socket, data, callback) {
      callback(null, true);
   },


   processNewsong: function (socket, data, callback) {
      callback(null, true);
   },


   processUpdateVotes: function (socket, data, callback) {
      var listeners = data.room.metadata.$get('listeners');
      var upvotes   = data.room.metadata.$get('upvotes');
      var downvotes = data.room.metadata.$get('downvotes');

      socket.get('currentSong', function (err, currentSong) {
         self.db['song.getId'](currentSong.id, function (err, dbSongId) {
            self.db['user.getId'](currentSong.current_dj, function (err, dbCurrentDjId) {
               socket.get('room', function (err, roomid) {
                  var roomid         = roomid;
                  var name           = null;
                  var description    = null;
                  var shortcut       = null;
                  var moderator_id   = null;
                  var current_dj     = dbCurrentDjId;
                  var song_starttime = null;
                  var song_id        = null;

                  // Update room infos
                  self.db['room.create'](roomid, name, description, shortcut, moderator_id, current_dj, listeners, downvotes, upvotes, song_starttime, song_id, function(err, dbRoomId) {
                     // Create/Update song log
                     self.db['songLog.create'](dbRoomId, dbSongId, currentSong.starttime, downvotes, upvotes, dbCurrentDjId, true, function (err, songLogId) {
                        // Create/Update votes
                        if (data.room.metadata.votelog) {
                           for (var i=0; i<data.room.metadata.votelog.length; i++) {
                              var vote       = data.room.metadata.votelog[i];
                              var userid     = vote[0];
                              var appreciate = vote[1];
                              self.db['user.getId'](userid, function(err, dbUserId, params) {
                                 var appreciate = params.appreciate;
                                 self.db['vote.create'](dbUserId, dbSongId, currentSong.starttime, dbRoomId, appreciate, function (err, voteId) {
                                 });
                              }, { appreciate: appreciate });
                           }
                        }
                     });
                  });
               });
            });
         });
      });
   },


   processSpeak: function (socket, data, callback) {
      var userid  = data.userid;
      var name    = data.name;
      var text    = data.text;
      socket.get('room', function (err, roomid) {
         self.db['user.getId'](userid, function (err, dbUserId) {
            self.db['room.getId'](roomid, function (err,dbRoomId) {
               self.db['chat.create'](dbUserId, name, text, dbRoomId, function (err, res) {
                  callback(null, true);
               });
            });
         });
      });
   },


   processRoomInfos: function (socket, data, callback) {
      // Create/Update room
      var msgid         = data.$get('msgid');
      var room          = data.$get('room');
      var metadata      = room.$get('metadata');
      var current_song  = metadata.$get('current_song');

      var created       = new Date(room.created * 1000).toISOString();
      var name          =     room.$get('name');
      var shortcut      =     room.$get('shortcut');
      var description   =     room.$get('description');
      var roomid        =     room.$get('roomid');
      var current_dj    = metadata.$get('current_dj');
      var listeners     = metadata.$get('listeners');
      var downvotes     = metadata.$get('downvotes');
      var upvotes       = metadata.$get('upvotes');
      if (current_song) {
         var starttime  = new Date(current_song.starttime * 1000).toISOString();
         var songid    = current_song.$get('_id');
      } else {
         var starttime  = null;
         var songid    = null;
      }

      var dbSongId = null;

      self.db['user.get'](current_dj, function (err, currentDj) {
         if (!currentDj) { currentDj = { id: null, name: null }; }
         self.db['song.get'](songid, function (err, currentSong) {
            if (!currentSong) { currentSong = { id: null, name: null, starttime: null }; }
            self.db['room.createUpdate'](roomid, name, created, description, shortcut, currentDj.id,
                                   currentDj.name, listeners, upvotes, downvotes, currentSong.id,
                                   currentSong.name, currentSong.starttime,
                                   function (err, roomObj) {

               for (var i=0, len=data.users.length; i<len; i++) {
                  var user      = data.users[i];
                  var userid    = user.userid;
                  var user_name = user.name;
                  var created   = new Date(user.created * 1000).toISOString();
                  var laptop    = user.laptop;
                  var acl       = user.acl;
                  var fans      = user.fans;
                  var points    = user.points;
                  var avatarid  = user.avatarid;
                  self.db['user.createUpdate'](userid, user_name, created, laptop, acl, fans,
                                               points, avatarid, function (err, userObj) { });
               }

               for (var i=0; i<data.room.metadata.songlog.length; i++) {
                  var song      = data.room.metadata.songlog[i];
                  var songid    = song.$get('_id');
                  var album     = song.metadata.$get('album');
                  var artist    = song.metadata.$get('artist');
                  var coverart  = song.metadata.$get('coverart');
                  var song_name = song.metadata.$get('song');
                  var length    = song.metadata.$get('length');
                  var mnid      = song.metadata.$get('mnid');
                  var genre     = song.metadata.$get('genre');
                  var filepath  = song.metadata.$get('filepath');
                  var bitrate   = song.metadata.$get('bitrate');

                  self.db['song.createUpdate'](songid, album, artist, song_name,
                                               coverart, length, mnid, genre,
                                               filepath, bitrate, function (err, songObj) { });
               }

               socket.set('room', { id: roomObj.id, roomid: roomObj.roomid });

               if (songid) {
                  self.db['song.get'](songid, function (err, songObj) {
                     if (!songObj) { songObj = { id: null, name: null, starttime: null }; }
                     self.db['room.createUpdate'](roomid, name, created, description, shortcut,
                                                  currentDj.id, currentDj.name, listeners, upvotes,
                                                  downvotes, songObj.id, songObj.song,
                                                  songObj.starttime,
                                                  function (err, room) {
                        socket.set('currentSong', { id: songObj.id, songid: songObj.songid,
                                                    starttime: songObj.starttime,
                                                    current_dj: current_dj }, function () {
                           callback(null, true);
                        });
                     });
                  });
               } else {
                  socket.set('currentSong', { id: null, songid: null, starttime: null,
                                              current_dj: current_dj });
                  callback(null, true);
               }
            });
         });
      });
   },


   processRooms: function (socket, data, callback) {
      socket.set('room', null, function () {
         callback(null, 'stop');
      });
   }
};

exports.sockets = sockets;
