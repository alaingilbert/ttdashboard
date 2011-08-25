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
            console.log('DATA RECEIVE', data);
            // TODO: Implement this
         } else { callback('Not authenticated', null); socket.disconnect(); } });
      });


      socket.on('disconnect', function () {
      });
   },
};

exports.sockets = sockets;
