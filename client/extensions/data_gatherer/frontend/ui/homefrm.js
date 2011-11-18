var HomeFrm = new Class(Frame, {
   initialize: function (data) {
      this.$super(data);
      var menu = { 
                 };
      var menuElem = { display:            'block'
                     , width:              '240px'
                     , height:             '10px'
                     , color:              '#666'
                     , padding:            '5px 5px 10px 5px'
                     , cursor:             'pointer'
                     , 'background-color': '#fff'
                     , 'border-bottom':    '1px solid #ccc'
                     };
      var events = { mouseover: function () { this.setStyle('background-color', '#eee'); }
                   , mouseout:  function () { this.setStyle('background-color', '#fff'); }
                   };
      var ul = new Element('ul')
         .insertTo(this);

      this.playlistsBtn = new Element('li')
         .setStyle(menuElem)
         .text('Playlists')
         .on(events)
         .insertTo(ul);

      this.aboutBtn = new Element('li')
         .setStyle(menuElem)
         .text('About')
         .on(events)
         .insertTo(ul);
   }
});
