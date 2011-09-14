// Inject the script on turntable
document.body.appendChild(document.createElement('script')).src=chrome.extension.getURL("frontend/turntable.js");

// Inject the div for the communication
var data_gatherer = document.createElement('div');
data_gatherer.id = 'data_gatherer';
data_gatherer.style.display = 'none';
var data_receiver = document.createElement('div');
data_receiver.id = 'data_receiver';
data_receiver.style.display = 'none';
document.body.appendChild(data_gatherer);
document.body.appendChild(data_receiver);

var receiverEvent = document.createEvent('Event');
receiverEvent.initEvent('myReceiverEvent', true, true)

// Communicate with the extension
var port = chrome.extension.connect();
document.getElementById('data_gatherer').addEventListener('myCustomEvent', function() {
   var eventData = document.getElementById('data_gatherer').innerText;
   port.postMessage( eventData );
});


chrome.extension.sendRequest({ action: 'setTurntableTab' });

chrome.extension.onRequest.addListener(function (request, sender, callback) {
   switch (request.action) {
      case 'setPlaylist':
         var playlist = request.playlist;
         data_receiver.innerText = JSON.stringify(playlist);
         data_receiver.dispatchEvent(receiverEvent);
         break;
   }
});
