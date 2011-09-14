var Popup = new Class(Element, {
   initialize: function () {
      this.$super('div');
      this.setStyle({ width:  '250px'
                    , height: '400px'
                    });

      var middle  = new Middle().insertTo(this);

      var prevBtn = new PrevBtn().insertTo(this);
      prevBtn.on('click', function (evt) {
         var left = middle.win.getStyle('left').replace('px', '');
         var nb = Math.abs(left / 250);
         if (nb > 0) {
            middle.win.morph({ left: ((nb-1) * -250)+'px' });
         }
      });

      this.insertTo(document.body);
   }
});
