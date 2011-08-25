var scrollDown = false;
document.addEventListener('mousewheel', function (evt) {
   var menu = document.getElementById('menu');

   // Scroll down
   if (evt.wheelDelta < 0) {
      if (!scrollDown) {
         menu.style.position = 'absolute';
         menu.style.top = (window.scrollY + menu.offsetTop) + 'px';
      }
      scrollDown = true;
      if (window.scrollY + window.innerHeight > menu.offsetTop + menu.offsetHeight) {
         menu.style.position = 'fixed';
         menu.style.top = '';
         menu.style.bottom = '0px';
      }

   // Scroll up
   } else {
      if (scrollDown) {
         menu.style.position = 'absolute';
         menu.style.top = (window.scrollY + menu.offsetTop) + 'px';
      }
      scrollDown = false;
      if (window.scrollY < menu.offsetTop) {
         menu.style.position = 'fixed';
         menu.style.top = '0px';
         menu.style.bottom = '';
      }
   }
}, false);
