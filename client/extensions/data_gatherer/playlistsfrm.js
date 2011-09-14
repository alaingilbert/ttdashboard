var PlaylistsFrm = new Class(Frame, {
   initialize: function (data) {
      this.$super(data);

      var header = new Element('div')
         .setStyle({ height: '40px' })
         .insertTo(this);


      var title  = new Element('h1')
         .text('My playlists')
         .setStyle({ float:        'left'
                   , width:        '185px'
                   , overflow:     'hidden'
                   , 'margin': '10px 0 0 5px'
                   })
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

      new Element('ul').insertTo(body);
   }
});
