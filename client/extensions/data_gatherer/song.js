var Song = new Class(Element, {
   initialize: function (data) {
      this.$super('li');
      this.setStyle({ width:              '250px'
                    , 'border-bottom':    '1px solid #ccc'
                    , 'background-color': '#fff'
                    })
         .on({ mouseover: function (evt) { this.setStyle('background-color', '#eee'); }
             , mouseout:  function (evt) { this.setStyle('background-color', '#fff'); }
             });

      var coverart = new Element('img')
         .set('src', data.coverart)
         .setStyle({ width:  '30px',
                     height: '30px',
                     margin: '5px',
                     float:  'left' })
         .insertTo(this);

      var infos = new Element('div')
         .setStyle({ float: 'left'
                   , width: '200px'
                   })
         .insertTo(this);

      var text = new Element('span')
         .text(data.song)
         .setStyle({ width:        '200px'
                   , height:       '15px'
                   , overflow:     'hidden'
                   , display:      'block'
                   , 'font-size':  '14px'
                   , 'margin-top': '5px'
                   })
         .insertTo(infos);

      var artist = new Element('span')
         .text(data.artist)
         .setStyle({ width:        '200px'
                   , display:      'block'
                   , color:        '#777'
                   , 'font-size':  '12px'
                   , 'margin-top': '5px'
                   })
         .insertTo(infos);

      var clear = new Element('div')
         .setStyle({ clear: 'both' })
         .insertTo(this);

      this.data = data;
   }
});
