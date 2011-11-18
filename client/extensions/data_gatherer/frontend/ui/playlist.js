var Playlist = new Class(Element, {
   initialize: function (data) {
      this.$super('li');
      this.setStyle({ width:              '250px'
                    , 'border-bottom':    '1px solid #ccc'
                    , 'background-color': '#fff'
                    })
         .on({ mouseover: function (evt) { this.setStyle('background-color', '#eee'); }
             , mouseout:  function (evt) { this.setStyle('background-color', '#fff'); }
             });

      var text = new Element('span')
         .text(data.name)
         .setStyle({ width:        '240px'
                   , height:       '10px'
                   , color:        '#666'
                   , overflow:     'hidden'
                   , display:      'block'
                   , cursor:       'pointer'
                   , padding:      '5px 5px 10px 5px'
                   , 'font-size':  '14px'
                   })
         .insertTo(this);

      this.data = data;
   }
});
