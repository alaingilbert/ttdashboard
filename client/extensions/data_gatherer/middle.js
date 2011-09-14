var Middle = new Class(Element, {
   initialize: function () {
      var self = this;
      this.$super('div');
      this.setStyle({ width:    '250px'
                    , height:   '360px'
                    , position: 'relative'
                    , overflow: 'hidden'
                    , left:     '0px'
                    });


      this.win = new Element('div')
         .setStyle({ width:    '250px'
                   , height:   '360px'
                   , position: 'relative'
                   , left:     '0px'
                   })
         .insertTo(this);

      var homeFrm      = new      HomeFrm({ x: 0,   y: 0 }).insertTo(this.win);
      var aboutFrm     = new        Frame({ x: 250, y: 0 }).insertTo(this.win);
      var playlistsFrm = new PlaylistsFrm({ x: 250, y: 0 }).insertTo(this.win);
      var playlistFrm  = new  PlaylistFrm({ x: 500, y: 0 }).insertTo(this.win);

      homeFrm.playlistsBtn.on('click', function (evt) {
         chrome.extension.sendRequest({ action: 'getPlaylists' }, function (data) {
            playlistsFrm.first('ul').clean();
            for (var i=0; i<data.playlists.length; i++) {
               var playlist = new Playlist(data.playlists[i])
                  .on('click', function (evt) {
                     var req = { action: 'getPlaylist', playlistId: this.data.id };
                     chrome.extension.sendRequest(req, function (data) {
                        playlistFrm.data = data;
                        playlistFrm.first('ul').clean();
                        for (var i=0; i<data.songs.length; i++) {
                           var song = new Song(data.songs[i]);
                           playlistFrm.first('ul').insert(song);
                        }
                        playlistFrm.focus();
                     });
                  });
               playlistsFrm.first('ul').insert(playlist);
            }
            playlistsFrm.focus();
         });
      })
   }
});
