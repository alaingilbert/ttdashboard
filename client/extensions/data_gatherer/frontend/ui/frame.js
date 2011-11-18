var Frame = new Class(Element, {
   initialize: function (data) {
      this.$super('div');
      this.setStyle({ width:     '250px'
                    , height:    '360px'
                    , position:  'absolute'
                    , overflow:  'hidden'
                    , left:      data.x+'px'
                    , top:       data.y+'px'
                    , 'z-index': '0'
                    });
   },

   focus: function () {
      var left = this.getStyle('left').replace('px', '');
      this.parent().morph({ left: -left+'px' });
   }
});
