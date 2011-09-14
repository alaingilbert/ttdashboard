var PrevBtn = new Class(Element, {
   initialize: function () {
      this.$super('a');
      this.setStyle({ position:           'fixed'
                    , left:               '5px'
                    , bottom:             '5px'
                    , display:            'block'
                    , width:              '25px'
                    , height:             '22px'
                    , border:             '1px solid gray'
                    , cursor:             'pointer'
                    , 'text-align':       'center'
                    , 'padding-top':      '3px'
                    , 'border-radius':    '15px'
                    , 'background-color': '#eee'
                    });
   
      this.on({ mouseover: this.onMouseOver
              , mouseout:  this.onMouseOut
              });

      this.html('&laquo;');
   },


   onMouseOver: function () {
      this.setStyle({ 'background-color': '#ccc' });
   },


   onMouseOut: function () {
      this.setStyle({ 'background-color': '#eee' });
   }
});
