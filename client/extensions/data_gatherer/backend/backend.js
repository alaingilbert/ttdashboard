var ws = io.connect('http://127.0.0.1:8000/');


ws.emit('auth', { apiKey: '0000000000000000000000000000000000000000' }, function (err, succeed) {
   if (!err && succeed) {
      setInterval(function () {
         ws.emit('data', { action: 'test', msg: 'msg' }, function (err, succeed) { console.log(err, succeed); });
      }, 1000);
   }
});


chrome.extension.onConnect.addListener(function(port) {
  port.onMessage.addListener(function(data) {
     ws.emit('data', data);
  });
});
