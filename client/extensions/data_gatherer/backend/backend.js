var ws = io.connect('http://127.0.0.1:9000/');


ws.emit('auth', { apiKey: '0000000000000000000000000000000000000000' }, function (err, succeed) {
   if (!err && succeed) {
      chrome.extension.onConnect.addListener(function(port) {
         port.onMessage.addListener(function(data) {
            ws.emit('data', JSON.parse(data), function (err, res) {
               console.log(err, res);
            });
         });
      });
   }
});
