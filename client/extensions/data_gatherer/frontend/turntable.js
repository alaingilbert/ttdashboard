var customEvent = document.createEvent('Event');
customEvent.initEvent('myCustomEvent', true, true)

var data_gatherer = document.getElementById('data_gatherer');


function message(data) {
   data_gatherer.innerText = JSON.stringify(data);
   data_gatherer.dispatchEvent(customEvent);
}

turntable.addEventListener('message', message);
