//var ws = io.connect('http://50.22.244.52:9000/');
var ws = io.connect('http://127.0.0.1:9000/');


var states       = { stopp: 0, idle: 1, work: 2 };
var state        = states.work;
var bandwidth    = 0;
var turntableTab = null;


ws.emit('auth', { apiKey: '9be0dacffac1ea5b0334a59b0f5cb03bfe9ce102' }, function (err, succeed) {
   if (!err && succeed) {
      start();
   }
});


function start() {
   chrome.extension.onConnect.addListener(function (port) {
      port.onMessage.addListener(function (data) {
         var params = JSON.parse(data);
         if (state == states.work) {
            bandwidth += data.length;
            ws.emit('data', params, function (err, res) {
               console.log(err, res);
            });
         } else {
            if (!params.command) {
               if ((params.msgid && params.room) ||
                    params.rooms) {
                  bandwidth += data.length;
                  ws.emit('data', params, function (err, res) {
                     console.log(err, res);
                  });
               }
            }
         }
      });
   });
}


ws.on('startt', function (data) {
   console.log('startt');
   state = states.work;
});


ws.on('stopp', function (data) {
   console.log('stopp');
   state = states.stopp;
});


function onRequest(request, sender, callback) {
   switch (request.action) {


      case 'setTurntableTab':
         turntableTab = sender.tab.id;
         break;


      case 'getPlaylists':
         ws.emit('getPlaylists', { }, function (err, res) {
            callback(res);
         });
         break;


      case 'getPlaylist':
         var playlistId = request.playlistId;
         ws.emit('getPlaylist', { playlistId: playlistId }, function (err, res) {
            callback(res);
         });
         break;


      case 'setPlaylist':
         var playlist = request.playlist;
         chrome.tabs.sendRequest(turntableTab, { action: 'setPlaylist', playlist: playlist }, function () {
            callback();
         });
         break;
   }
}


function onRemoved(tabId) {
   if (turntableTab == tabId) {
      turntableTab = null;
   }
}


chrome.extension.onRequest.addListener(onRequest);
chrome.tabs.onRemoved.addListener(onRemoved);
