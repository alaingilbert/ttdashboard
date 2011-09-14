var customEvent = document.createEvent('Event');
customEvent.initEvent('myCustomEvent', true, true)

var data_gatherer = document.getElementById('data_gatherer');
var data_receiver = document.getElementById('data_receiver');

data_receiver.addEventListener('myReceiverEvent', function () {
   var eventData = document.getElementById('data_receiver').innerText;
   var data = JSON.parse(eventData).songs;

   // Remove the current playlist
   var files = turntable.playlist.files;
   var arr = [];
   for (var i=0, len=files.length; i<len; i++) {
      arr.push(files[i].fileId);
   }
   function remRec(arr) {
      var fileId = arr.splice(0, 1)[0];
      turntable.playlist.removeFile(fileId);
      if (arr.length > 0) {
         setTimeout(remRec(arr), 300);
      } else {
         addSongsRec(data);
      }
   }

   if (arr.length > 0) {
      remRec(arr);
   } else {
      addSongsRec(data);
   }

   function addSongsRec(songs) {
      var song = songs.splice(0, 1)[0];
      turntable.playlist.addSong({ fileId: song.songid, metadata: song });
      if (songs.length > 0) {
         setTimeout(addSongsRec(songs), 300);
      }
   }
});


function message(data) {
   data_gatherer.innerText = JSON.stringify(data);
   data_gatherer.dispatchEvent(customEvent);
}

turntable.addEventListener('message', message);
