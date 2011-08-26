// Inject the script on turntable
document.body.appendChild(document.createElement('script')).src=chrome.extension.getURL("frontend/turntable.js");

// Inject the div for the communication
document.body.appendChild(document.createElement('div')).id='data_gatherer';

// Communicate with the extension
var port = chrome.extension.connect();
document.getElementById('data_gatherer').addEventListener('myCustomEvent', function() {
   var eventData = document.getElementById('data_gatherer').innerText;
   port.postMessage( eventData );
});
