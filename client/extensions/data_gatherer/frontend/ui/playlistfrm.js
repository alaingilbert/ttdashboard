var PlaylistFrm = new Class(Frame, {
   initialize: function (data) {
      var self = this;
      this.$super(data);
      this.data = null;


      var header = new Element('div')
         .setStyle({ height: '40px' })
         .insertTo(this);


      var title  = new Element('h1')
         .text('TEST')
         .setStyle({ float:        'left'
                   , width:        '185px'
                   , overflow:     'hidden'
                   , 'margin': '10px 0 0 5px'
                   })
         .insertTo(header);


      var importBtn = new Element('div')
         .on({ click: function (evt) { chrome.extension.sendRequest({ action: 'setPlaylist', playlist: self.data }); } })
         .addClass('button')
         .addClass('greenBtn')
         .addClass('small')
         .setStyle({ float: 'left'
                   , 'margin-top': '10px'
                   })
         .text('Import')
         .insertTo(header);


      var body = new Element('div')
         .setStyle({ width:    '250px'
                   , height:   '320px'
                   , position: 'absolute'
                   , overflow: 'hidden'
                   })
         .on({ mousewheel: function (evt) {
                  var delta = evt._.wheelDelta;
                  this.scrollTo(0, this.scrolls().y - delta);
                  evt.stopPropagation();
                  evt.preventDefault();
               }
             })
         .insertTo(this);


      var ul = new Element('ul').insertTo(body);
   }
});
