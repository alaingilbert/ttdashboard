/**
 * Similar tot the .update in python.
 */
Object.defineProperty(Object.prototype, "$update", {
   enumerable: false,
   value: function(from) {
      var props = Object.getOwnPropertyNames(from);
      var dest = this;
      props.forEach(function(name) {
         if (name in dest) {
            var destination = Object.getOwnPropertyDescriptor(from, name);
            Object.defineProperty(dest, name, destination);
         }
      });
      return this;
   }
});


/**
 * Similar to the .get in python.
 */
Object.defineProperty(Object.prototype, '$get', {
   value: function (name, def) {
      if (def === undefined) { def = null; }
      return this[name] !== undefined ? this[name] : def;
   }
});
