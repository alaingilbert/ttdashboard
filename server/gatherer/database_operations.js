var DatabaseOperations = {

   db: null,
   setDatabase: function (database) { this.db = database; },


   /**
    * Create/update a user.
    * @sig userid:string, name:string, created:date, laptop:string, acl:int, fans:int, points:int, avatarid:int, callback:fn -> User:obj
    */
   'user.createUpdate': function () {
      var self = this;

      if (arguments.length !== 9) { throw new Error('user.createUpdate - Bad arguments length'); }
      if (typeof arguments[8] !== 'function') { throw new Error('user.createUpdate - Arguments invalid'); }

      var userid   = arguments[0]
        , name     = arguments[1]
        , created  = arguments[2]
        , laptop   = arguments[3]
        , acl      = arguments[4]
        , fans     = arguments[5]
        , points   = arguments[6]
        , avatarid = arguments[7]
        , callback = arguments[8];

      if (typeof userid    !== 'string' ||
          typeof name      !== 'string' ||
          (typeof created  !== 'object' && typeof created !== 'string') ||
          typeof laptop    !== 'string' ||
          typeof acl       !== 'number' ||
          typeof fans      !== 'number' ||
          typeof points    !== 'number' ||
          typeof avatarid !== 'number') {
         return callback('user.createUpdate - Arguments invalid', null);
      }

      if (fans   < 0) { fans   = 0; }
      if (points < 0) { points = 0; }

      var query  = 'SELECT id FROM users WHERE userid=$1 LIMIT 1';
      var params = [userid];

      self.db.query(query, params, function (err, res) {
         if (res.rowCount == 1) {
            var query  = 'UPDATE users SET name=$1, laptop=$2, acl=$3, fans=$4, points=$5, avatarid=$6 ' +
                         'WHERE id=$7 RETURNING *';
            var params = [name, laptop, acl, fans, points, avatarid, res.rows[0].id];
            self.db.query(query, params, function (err, res) {
               callback(null, res.rows[0]);
            });
         } else {
            var query  = 'INSERT INTO users (userid, name, created, laptop, acl, fans, points, avatarid) ' +
                         'VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING *';
            var params = [userid, name, created, laptop, acl, fans, points, avatarid];
            self.db.query(query, params, function (err, res) {
               callback(null, res.rows[0]);
            });
         }
      });
   },


   /**
    * Get a user.
    * @sig id:int, callback:fn -> User:obj
    * @sig userid:string, callback:fn -> User:obj
    */
   'user.get': function () {
      var self = this;

      if (arguments.length !== 2) { throw new Error('user.get - Bad arguments length'); }
      if (typeof arguments[1] !== 'function') { throw new Error('user.get - Arguments invalid'); }

      var field    = arguments[0]
        , callback = arguments[1];

      if (typeof field === 'number') {
         var query  = 'SELECT * FROM users WHERE id=$1 LIMIT 1';
         var params = [ field ];
      } else if (typeof field === 'string') {
         var query  = 'SELECT * FROM users WHERE userid=$1 LIMIT 1';
         var params = [ field ];
      } else {
         return callback('user.createUpdate - Arguments invalid', null);
      }

      self.db.query(query, params, function (err, res) {
         if (res.rowCount == 1) {
            callback(null, res.rows[0]);
         } else {
            callback(null, null);
         }
      });
   },


   /**
    * This method create a chat message.
    * @sig userId:int, roomId:int, name:string, text:string, callback:fn -> Message:obj
    */
   'chat.create': function () {
      var self = this;

      if (arguments.length !== 5) { throw new Error('chat.create - Bad arguments length'); }
      if (typeof arguments[4] !== 'function') { throw new Error('chat.create - Arguments invalid'); }

      var userId   = arguments[0]
        , roomId   = arguments[1]
        , name     = arguments[2]
        , text     = arguments[3]
        , callback = arguments[4];

      if (typeof userId !== 'number' ||
          typeof roomId !== 'number' ||
          typeof name   !== 'string' ||
          typeof text   !== 'string') {
         return callback('chat.create - Arguments invalid', null);
      }

      var query  = 'INSERT INTO chatlog (userid, roomid, name, text) ' +
                   'VALUES ($1, $2, $3, $4) RETURNING *';
      var params = [userId, roomId, name, text];
      self.db.query(query, params, function(err, res) {
         if (!err) {
            var message = res.rows[0];
            callback(null, message);
         } else {
            callback(err, null);
         }
      });
   },


   /**
    * Create/update a room.
    * @sig 
    */
   'room.createUpdate': function () {
      var self = this;

      if (arguments.length !== 14) { throw new Error('user.createUpdate - Bad arguments length'); }
      if (typeof arguments[13] !== 'function') { throw new Error('user.createUpdate - Arguments invalid'); }

      var roomid               = arguments[0]
        , name                 = arguments[1]
        , created              = arguments[2]
        , description          = arguments[3]
        , shortcut             = arguments[4]
        , currentDjId          = arguments[5]
        , currentDjName        = arguments[6]
        , listeners            = arguments[7]
        , upvotes              = arguments[8]
        , downvotes            = arguments[9]
        , currentSongId        = arguments[10]
        , currentSongName      = arguments[11]
        , currentSongStarttime = arguments[12]
        , callback             = arguments[13];

      if (typeof roomid                !== 'string' ||
          typeof name                  !== 'string' ||
          (typeof created              !== 'object' && typeof created       !== 'string') ||
          (typeof description          !== 'string' && description          !== null) ||
          (typeof shortcut             !== 'string' && shortcut             !== null) ||
          (typeof currentDjId          !== 'number' && currentDjId          !== null) ||
          (typeof currentDjName        !== 'string' && currentDjName        !== null) ||
          typeof listeners             !== 'number' ||
          typeof upvotes               !== 'number' ||
          typeof downvotes             !== 'number' ||
          (typeof currentSongId        !== 'number' && currentSongId        !== null) ||
          (typeof currentSongName      !== 'string' && currentSongName      !== null) ||
          (typeof currentSongStarttime !== 'object' && currentSongStarttime !== null)) {
         return callback('room.createUpdate - Arguments invalid', null);
      }

      var query  = 'SELECT id FROM rooms WHERE roomid=$1 LIMIT 1';
      var params = [roomid];

      self.db.query(query, params, function (err, res) {
         if (res.rowCount == 1) {
            var query  = 'UPDATE rooms SET current_dj=$1, current_dj_name=$2, ' +
                         '    listeners=$3, upvotes=$4, downvotes=$5,         ' +
                         '    current_song=$6, current_song_name=$7,          ' +
                         '    song_starttime=$8                               ' +
                         'WHERE id=$9 RETURNING *';
            var params = [ currentDjId, currentDjName, listeners, upvotes, downvotes,
                           currentSongId, currentSongName, currentSongStarttime,
                           res.rows[0].id ];
            self.db.query(query, params, function (err, res) {
               callback(null, res.rows[0]);
            });
         } else {
            var query  = 'INSERT INTO rooms (roomid, name, created, description,   ' +
                         '    shortcut, current_dj, current_dj_name, listeners,    ' +
                         '    upvotes, downvotes, current_song, current_song_name, ' +
                         '    song_starttime)                                      ' +
                         'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) RETURNING *';
            var params = [roomid, name, created, description, shortcut,
                          currentDjId, currentDjName, listeners, upvotes,
                          downvotes, currentSongId, currentSongName, currentSongStarttime];
            self.db.query(query, params, function (err, res) {
               callback(null, res.rows[0]);
            });
         }
      });
   },


   /**
    * Create/update a user.
    * @sig userid:string, name:string, created:date, laptop:string, acl:int, fans:int, points:int, avatarid:int, callback:fn -> User:obj
    */
   'song.createUpdate': function () {
      var self = this;

      if (arguments.length !== 11) { throw new Error('song.createUpdate - Bad arguments length'); }
      if (typeof arguments[10] !== 'function') { throw new Error('song.createUpdate - Arguments invalid'); }

      var songid   = arguments[0]
        , album    = arguments[1]
        , artist   = arguments[2]
        , song     = arguments[3]
        , coverart = arguments[4]
        , length   = arguments[5]
        , mnid     = arguments[6]
        , genre    = arguments[7]
        , filepath = arguments[8]
        , bitrate  = arguments[9]
        , callback = arguments[10];

      console.log('CRISS 1', coverart, typeof coverart);
      if (typeof songid    !== 'string' ||
          (typeof album    !== 'string' && album    !== null) ||
          (typeof artist   !== 'string' && artist   !== null) ||
          (typeof song     !== 'string' && song     !== null) ||
          (typeof coverart !== 'string' && coverart !== null) ||
          typeof length    !== 'number' ||
          (typeof mnid     !== 'number' && mnid     !== null) ||
          (typeof genre    !== 'string' && genre    !== null) ||
          (typeof filepath !== 'string' && filepath !== null) ||
          (typeof bitrate  !== 'number' && bitrate  !== null)) {
         console.log('SACRAMENT', coverart);
         return callback('song.createUpdate - Arguments invalid', null);
      }
      console.log('CRISS 2', coverart);

      var query  = 'SELECT * FROM songs WHERE songid=$1 LIMIT 1';
      var params = [ songid ];

      self.db.query(query, params, function (err, res) {
         if (res.rowCount == 1) {
            callback(null, res.rows[0]);
         } else {
            var query  = 'INSERT INTO songs (songid, album, artist, song, coverart, ' +
                         '    length, mnid, genre, filepath, bitrate) ' +
                         'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING *';
            var params = [ songid, album, artist, song, coverart, length, mnid, genre,
                           filepath, bitrate ];
            self.db.query(query, params, function (err, res) {
               callback(null, res.rows[0]);
            });
         }
      });
   },


   /**
    * Get a song.
    * @sig id:int, callback:fn -> Song:obj
    * @sig songid:string, callback:fn -> Song:obj
    */
   'song.get': function () {
      var self = this;

      if (arguments.length !== 2) { throw new Error('song.get - Bad arguments length'); }
      if (typeof arguments[1] !== 'function') { throw new Error('song.get - Arguments invalid'); }

      var field    = arguments[0]
        , callback = arguments[1];

      if (typeof field === 'number') {
         var query  = 'SELECT * FROM songs WHERE id=$1 LIMIT 1';
         var params = [field];
      } else if (typeof field === 'string') {
         var query  = 'SELECT * FROM songs WHERE songid=$1 LIMIT 1';
         var params = [field];
      } else {
         return callback('song.createUpdate - Arguments invalid', null);
      }

      self.db.query(query, params, function (err, res) {
         if (res.rowCount == 1) {
            callback(null, res.rows[0]);
         } else {
            callback(null, null);
         }
      });
   },




   /**
    * This method create/update a song.
    * @sig songid:string, album:string, artist:string, coverart:string, song:string, length:int, mnid:int, genre:string, filepath:string, bitrate:int, nb_play:int, callback:fn -> id:int
    */
   'song.create': function(songid, album, artist, coverart, song, length, mnid, genre, filepath, bitrate, nb_play, callback) {
      var self   = this;
      var query  = "INSERT INTO songs (songid, album, artist, coverart, song, length, mnid, genre, filepath, bitrate, nb_play) " +
                   "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)                     ";
      var params = [songid, album, artist, coverart, song, length, mnid, genre, filepath, bitrate, nb_play];
      self.db.query(query, params, function(err, res) {
         if (!err) {
            var id = res.insertId
            callback(null, id);
         } else {
            callback(err, null);
         }
      });
   },


   /**
    * This method create/update a songLog.
    * @sig roomId:int, songId:int, starttime:date, downvotes:int, upvotes:int, current_dj:?, override:bool, callback:fn -> id:int
    */
   'songLog.create': function(dbRoomId, dbSongId, starttime, downvotes, upvotes, current_dj, override, callback) {
      var self = this;
      var query = "SELECT * FROM songlog WHERE roomid=? AND songid=? AND starttime=?";
      var params = [dbRoomId, dbSongId, starttime];
      self.db.query(query, params, function(err, res) {
         if (!err) {
            if (res.length === 0) {
               var query  = "INSERT INTO songlog (roomid, songid, starttime, downvotes, upvotes, current_dj) " +
                            "VALUES (?, ?, ?, ?, ?, ?)                                                       ";
               var params = [dbRoomId, dbSongId, starttime, downvotes, upvotes, current_dj];
               self.db.query(query, params, function(err, res) {
                  if (!err) {
                     var id     = res.insertId
                     var query  = "UPDATE songs SET nb_play=nb_play+1 WHERE id=?";
                     var params = [dbSongId];
                     self.db.query(query, params, function(err, res) {
                        if (!err) {
                           callback(null, id);
                        } else {
                           callback(err, null);
                        }
                     });
                  } else {
                     callback(err, null);
                  }
               });
            } else {
               if (override) {
                  var query  = "UPDATE songlog SET downvotes=?, upvotes=? WHERE roomid=? AND songid=? AND starttime=?";
                  var params = [downvotes, upvotes, dbRoomId, dbSongId, starttime];
                  self.db.query(query, params, function(err, res) {
                     if (!err) {
                        var id = res.insertId
                        callback(null, id);
                     } else {
                        callback(err, null);
                     }
                  });
               }
            }
         }
      });
   },


   /**
    * Create a vote.
    * @sig userId:int, songId:int, starttime:date, roomId:int, appreciate:string, callback:fn -> id:int
    */
   'vote.create': function(dbUserId, dbSongId, starttime, dbRoomId, appreciate, callback) {
      var self = this;
      if (appreciate == 'up') {
         var query  = "INSERT INTO users_songs_liked (user_id, song_id, nb_awesomes, nb_lames, modified) " +
                      "VALUES (?, ?, 1, 0, NOW()) ON DUPLICATE KEY UPDATE nb_awesomes=nb_awesomes+1, modified=NOW()";
         var params = [dbUserId, dbSongId];
      } else if (appreciate == 'down') {
         var query  = "INSERT INTO users_songs_liked (user_id, song_id, nb_awesomes, nb_lames, modified) " +
                      "VALUES (?, ?, 0, 1, NOW()) ON DUPLICATE KEY UPDATE nb_lames=nb_lames+1, modified=NOW()";
         var params = [dbUserId, dbSongId];
      }

      self.db.query(query, params, function (err, res) {
         var query  = "INSERT INTO votes (userid, songid, starttime, roomid, created, appreciate) " +
                      "VALUES (?, ?, ?, ?, NOW(), ?) ON DUPLICATE KEY UPDATE appreciate=?, created=NOW()";
         var params = [dbUserId, dbSongId, starttime, dbRoomId, appreciate, appreciate];
         self.db.query(query, params, function(err, res) {
            if (!err) {
               var id = res.insertId
               callback(null, id);
            } else {
               callback(err, null);
            }
         });
      });
   },


   /**
    * Create a roomStat.
    * @sig roomId:int, listeners:int, djCount:int, currentDj:?, callback:fn -> id:int
    */
   'roomStat.create': function(dbRoomId, listeners, djcount, current_dj, created, callback) {
      var self   = this;
      var query  = "INSERT INTO room_stats (roomid, listeners, djcount, current_dj, created) " +
                   "VALUES (?, ?, ?, ?, ?)";
      var params = [dbRoomId, listeners, djcount, current_dj, created];
      self.db.query(query, params, function(err, res) {
         if (!err) {
            var id = res.insertId
            callback(null, id);
         } else {
            callback(err, null);
         }
      });
   },


   /**
    * Get a user id.
    * @sig userId:string, callback:fn -> userId:int
    */
   'user.getId': function(userid, callback, params) {
      var self   = this;
      var query  = "INSERT INTO users (userid)                   " +
                   "VALUES (?)                                   " +
                   "ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)";
      var params = [userid];
      self.db.query(query, params, function(err, res) {
         if (!err) {
            var id = res.insertId
            callback(null, id, params);
         } else {
            callback(err, null);
         }
      });
   },


   /**
    * Get a room id.
    * @sig roomId:string, callback:fn -> roomId:int
    */
   'room.getId': function(roomId, callback) {
      var self   = this;
      var query  = "INSERT INTO rooms (roomid)                   " +
                   "VALUES (?)                                   " +
                   "ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)";
      var params = [roomId];
      self.db.query(query, params, function(err, res) {
         if (!err) {
            var id = res.insertId
            callback(null, id);
         } else {
            callback(err, null);
         }
      });
   },


   /**
    * Get a song id.
    * @sig songId:string, callback:fn -> songId:int
    */
   'song.getId': function(songId, callback) {
      var self   = this;
      var query  = "INSERT INTO songs (songid)                   " +
                   "VALUES (?)                                   " +
                   "ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)";
      var params = [songId];
      self.db.query(query, params, function(err, res) {
         if (!err) {
            var id = res.insertId
            callback(null, id);
         } else {
            callback(err, null);
         }
      });
   }
};

exports.DatabaseOperations = DatabaseOperations
