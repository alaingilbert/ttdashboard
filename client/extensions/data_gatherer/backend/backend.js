var ws = io.connect('http://50.22.244.52:9000/');


var states = { stopp: 0, idle: 1, work: 2 };
var state  = states.work;
var bandwidth = 0;


ws.emit('auth', { apiKey: '0000000000000000000000000000000000000000' }, function (err, succeed) {
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
