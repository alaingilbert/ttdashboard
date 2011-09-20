require('./utils');

var Process = {
   db: null,
   setDb: function (db) { this.db = db; },

   /**
    * Process the data when a person came in the room.
    */
   registered: function (bot, data, callback) {
      var self = this;

      var user       = data.user[0];
      var userid     = user.$get('userid');
      var name       = user.$get('name');
      var created    = new Date(user.created * 1000).toISOString();
      var laptop     = user.$get('laptop');
      var acl        = user.$get('acl');
      var fans       = user.$get('fans');
      var points     = user.$get('points');
      var avatarid   = user.$get('avatarid');

      self.db['user.createUpdate'](userid, name, created, laptop, acl, fans,
                                   points, avatarid, function (err, userObj) { if (!err) {
         callback(null, true);
      } else { callback(err, null); } });
   },


   nosong: function (bot, data, callback) {
      var self = this;

      var djCount   = data.room.metadata.$get('djcount');
      var listeners = data.room.metadata.$get('listeners');

      // Get the informations about the room
      var sckRoom = bot.sckRoom;

      // Get the informations about the previous song
      var sckSong = bot.sckSong;
      // Create the song log
      self.db['songlog.create'](sckRoom.id, sckSong.id, sckSong.songName, sckSong.songArtist,
                                sckSong.songAlbum, sckSong.songCoverart, sckSong.songLength, sckSong.upvotes,
                                sckSong.downvotes, sckSong.djId, sckSong.djName, djCount,
                                listeners, function (err, log) { if (!err) {
         bot.sckSong = { id:           null
                       , songid:       null
                       , songName:     null
                       , songArtist:   null
                       , songAlbum:    null
                       , songCoverart: null
                       , songLength:   null
                       , upvotes:      null
                       , downvotes:    null
                       , djId:         null
                       , djName:       null
                       };
         callback(null, true);
      } else { return callback(err, null); } });
   },


   /**
    * Process the data when a new song start.
    */ 
   newsong: function (bot, data, callback) {
      var self = this;

      var room       = data.$get('room');
      var metadata   = room.$get('metadata');
      var song       = metadata.$get('current_song');
      var roomid     = room.$get('roomid');
      var songid     = song.$get('_id');
      var album      = song.metadata.$get('album');
      var artist     = song.metadata.$get('artist');
      var songName   = song.metadata.$get('song');
      var coverart   = song.metadata.$get('coverart');
      var length     = song.metadata.$get('length');
      var mnid       = song.metadata.$get('mnid');
      var genre      = song.metadata.$get('genre');
      var filepath   = song.metadata.$get('filepath');
      var bitrate    = song.metadata.$get('bitrate');
      var listeners  = metadata.$get('listeners');
      var currentDj  = metadata.$get('current_dj');
      var djCount    = metadata.$get('djcount');

      // Create and get the song
      self.db['song.createUpdate'](songid, album, artist, songName, coverart, length,
                                   mnid, genre, filepath,bitrate, function (err, songObj) { if (!err) {

      // Increment the nb_play counter of the song
      self.db['song.incrementNbPlay'](songid, function (err, res) { if (!err) {

      // Get the current dj
      self.db['user.get'](currentDj, function (err, djObj) { if (!err) {

      // Update informations of the room
      var update = { listeners: listeners
                   , upvotes: 0
                   , downvotes: 0
                   , current_song: songObj.id
                   , current_song_name: songName
                   , current_dj: djObj.id
                   , current_dj_name: djObj.name
                   };
      self.db['room.update'](roomid, update, function (err, roomObj) { if (!err) {

      // Get the informations about the room
      var sckRoom = bot.sckRoom;

      // Get the informations about the previous song
      var sckSong = bot.sckSong;

      if (sckRoom.current_song) {

         // Create the song log
         self.db['songlog.create'](sckRoom.id, sckSong.id, sckSong.songName, sckSong.songArtist,
                                   sckSong.songAlbum, sckSong.songCoverart, sckSong.songLength, sckSong.upvotes,
                                   sckSong.downvotes, sckSong.djId, sckSong.djName, djCount,
                                   listeners, function (err, log) { if (!err) {

         // Set the new informations about the current song
         bot.sckSong = { id:           songObj.id
                       , songid:       songObj.songid
                       , songName:     songObj.song
                       , songArtist:   songObj.artist
                       , songAlbum:    songObj.album
                       , songCoverart: songObj.coverart
                       , songLength:   songObj.length
                       , upvotes:      0
                       , downvotes:    0
                       , djId:         djObj.id
                       , djName:       djObj.name
                       };

         callback(null, true);

         } else { callback(err, null); } });
      
      } else {
         // Set the new informations about the current song
         bot.sckSong = { id:           songObj.id
                       , songid:       songObj.songid
                       , songName:     songObj.song
                       , songArtist:   songObj.artist
                       , songAlbum:    songObj.album
                       , songCoverart: songObj.coverart
                       , songLength:   songObj.length
                       , upvotes:      0
                       , downvotes:    0
                       , djId:         djObj.id
                       , djName:       djObj.name
                       };

         callback(null, true);
      }

      } else { callback(err, null); } });
      } else { callback(err, null); } });
      } else { callback(err, null); } });
      } else { callback(err, null); } });
   },


   /**
    * Process the data when a person vote.
    */
   updateVotes: function (bot, data, callback) {
      var self = this;
      var listeners = data.room.metadata.$get('listeners');
      var upvotes   = data.room.metadata.$get('upvotes');
      var downvotes = data.room.metadata.$get('downvotes');

      // Get the current song informations
      var currentSong = bot.sckSong;
      currentSong.upvotes   = upvotes;
      currentSong.downvotes = downvotes;

      var name           = null;
      var description    = null;
      var shortcut       = null;
      var moderator_id   = null;
      var currentDjId    = currentSong.djId;
      var currentDjName  = currentSong.djName;
      var song_id        = null;

      // Get the room informations
      var sckRoom = bot.sckRoom;

      // Update room infos
      var update = { upvotes: upvotes, downvotes: downvotes, listeners: listeners };
      self.db['room.update'](sckRoom.id, update, function (err, res) {

      // Create/Update song that users like
      var votes = data.room.metadata.votelog;
      function votelogRecurs(votes) {
         var vote       = votes.splice(0, 1)[0];
         var userid     = vote[0];
         var appreciate = vote[1];

         self.db['user.get'](userid, function(err, userObj) { if (!err) {

         // Create/Update how many time the user has liked
         self.db['userLike.create'](userObj.id, currentSong.id, appreciate, function (err, userLikeObj) {
            if (votes.length > 0) {
               votelogRecurs(votes);
            } else {
               callback(null, true);
            }
         });
         } else { callback(err, null); } });
      }

      votelogRecurs(votes);

      });
   },


   /**
    * Process the chat log.
    */
   speak: function (bot, data, callback) {
      var self = this;
      var userid  = data.userid;
      var name    = data.name;
      var text    = data.text;
      var room    = bot.sckRoom;
      self.db['user.get'](userid, function (err, user) { if (!err) {
         self.db['chat.create'](user.id, room.id, name, text, function (err, res) { if (!err) {
            callback(null, true);
         } else { return callback(err, null); } });
      } else { return callback(err, null); } });
   },


   /**
    * Process the data for the room infos.
    */
   roomInfos: function (bot, data, callback) {
      var self = this;
      // Create/Update room
      var msgid        = data.$get('msgid');
      var room         = data.$get('room');
      var metadata     = room.$get('metadata');
      var current_song = metadata.$get('current_song');
      var created      = new Date(room.created * 1000).toISOString();
      var name         =     room.$get('name');
      var shortcut     =     room.$get('shortcut');
      var description  =     room.$get('description');
      var roomid       =     room.$get('roomid');
      var current_dj   = metadata.$get('current_dj');
      var listeners    = metadata.$get('listeners');
      var downvotes    = metadata.$get('downvotes');
      var upvotes      = metadata.$get('upvotes');
      var songid       = null;
      if (current_song) {
         songid    = current_song.$get('_id');
      }

      self.db['user.get'](current_dj, function (err, currentDj) {
         var currentDjId   = null;
         var currentDjName = null;
         if (currentDj) {
            currentDjId   = currentDj.id;
            currentDjName = currentDj.name;
         }
         self.db['song.get'](songid, function (err, currentSong) {
            var currentSongId        = null;
            var currentSongName      = null;
            if (currentSong) {
               currentSongId        = currentSong.id;
               currentSongName      = currentSong.song;
            }
            self.db['room.createUpdate'](roomid, name, created, description, shortcut, currentDjId,
                                         currentDjName, listeners, upvotes, downvotes, currentSongId,
                                         currentSongName,
                                         function (err, roomObj) { if (!err) {

               function createUserRecurs (users) {
                  var user      = users.splice(0, 1)[0];
                  var userid    = user.userid;
                  var user_name = user.name;
                  var created   = new Date(user.created * 1000).toISOString();
                  var laptop    = user.laptop;
                  var acl       = user.acl;
                  var fans      = user.fans;
                  var points    = user.points;
                  var avatarid  = user.avatarid;
                  self.db['user.createUpdate'](userid, user_name, created, laptop, acl, fans,
                                               points, avatarid, function (err, userObj) { if (!err) {
                     if (users.length > 0) {
                        createUserRecurs(users);
                     } else {
                        step2();
                     }
                  } else { return callback(err, null); } });
               }

               if (data.users.length > 0) {
                  createUserRecurs(data.users);
               } else {
                  step2();
               }

               function step2 () {
                  var songs = data.room.metadata.songlog;

                  if (songs.length > 0) {
                     createSongRecurs(songs);
                  } else {
                     step3();
                  }
                  
                  function createSongRecurs (songs) {
                     var song      = songs.splice(0, 1)[0];
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
                                                  filepath, bitrate, function (err, songObj) {
                        if (songs.length > 0) {
                           createSongRecurs(songs);
                        } else {
                           step3();
                        }
                     });
                  }

                  function step3 () {
                     bot.sckRoom = { id: roomObj.id, roomid: roomObj.roomid };
                     if (songid) {
                        self.db['song.get'](songid, function (err, songObj) { if (!err) {
                           if (!songObj) { songObj = { id: null, name: null }; }
                           self.db['user.get'](current_dj, function (err, currentDj) {
                              var currentDjId   = null;
                              var currentDjName = null;
                              if (currentDj) {
                                 currentDjId   = currentDj.id;
                                 currentDjName = currentDj.name;
                              }
                              self.db['room.createUpdate'](roomid, name, created, description, shortcut,
                                                           currentDjId, currentDjName, listeners, upvotes,
                                                           downvotes, songObj.id, songObj.song,
                                                           function (err, room) {
                                 bot.sckSong = { id:           songObj.id
                                               , songid:       songObj.songid
                                               , songName:     songObj.song
                                               , songArtist:   songObj.artist
                                               , songAlbum:    songObj.album
                                               , songCoverart: songObj.coverart
                                               , songLength:   songObj.length
                                               , upvotes:      upvotes
                                               , downvotes:    downvotes
                                               , djId:         currentDjId
                                               , djName:       currentDjName
                                               };
                                 callback(null, true);
                              });
                           });
                        } else { callback(err, null); } });
                     } else {
                        bot.sckSong = { id:           null
                                      , songid:       null
                                      , songName:     null
                                      , songArtist:   null
                                      , songAlbum:    null
                                      , songCoverart: null
                                      , songLength:   null
                                      , upvotes:      null
                                      , downvotes:    null
                                      , djId:         null
                                      , djName:       null
                                      };
                        callback(null, true);
                     }
                  }
               }
            } else { return callback(err, null); } });
         });
      });
   }
};

module.exports = Process;
