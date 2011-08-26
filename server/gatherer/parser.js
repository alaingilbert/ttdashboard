//process.argv.forEach(function (val, index, array) { console.log(index + ': ' + val); });

var fs = require('fs');

(function () {


function slugify(text) {
   text = text.replace(/[^-a-zA-Z0-9,&\s]+/ig, '');
   text = text.replace(/-/gi, "_");
   text = text.replace(/\s/gi, "-");
   return text;
}


var DocGen = {
   
   
   filesArr: null,
   files: {},
   functions: [],
   nbLoaded: 0,


   init: function (files) {
      this.filesArr = files;
   },


   start: function () {
      for (var i=0, len=this.filesArr.length; i<len; i++) {
         var file = this.filesArr[i];
         this.processFile(file);
      }
   },


   fileLoaded: function() {
      this.nbLoaded++;
      if (this.nbLoaded == this.filesArr.length) {
         this.exportHtml();
      }
   },


   getSignatures: function (m) {
      var sig = null;
      var signatures = [];
      var rSig = /\\*\s?(@sig\s.*)\n/gi;
      while (sig = rSig.exec(m)) {
         var params = [];
         var rParam = /(\w+):(\w+)/gi;
         while (param = rParam.exec(sig[1])) {
            var name = param[1];
            var type = param[2];
            params.push({ name: name, type: type });
         }
         if (params.length >= 1) {
            ret = params.pop();
         }
         signatures.push({ params: params, ret: ret});
      }
      return signatures;
   },


   extractInfos: function (m) {
      var self = this;
      var fun = m[2];
      var rFun = /['|"]?([a-zA-Z0-9._-]+)['|"]?\s?:\s?function\s?\(.*\)\s?{/gi;
      var isFun = rFun.exec(fun);
      if (!isFun) {
         rFun = /socket\.on\(['|"]([a-zA-Z0-9._-]+)['|"]\s?,\s?function\s?\(.*\)\s?{/gi;
         isFun = rFun.exec(fun);
      }
      if (isFun) {
         var comment = m[1];
         var name = isFun[1];
         var sigs = self.getSignatures(comment);

         var desc = (/\*\s(.*?)\n/gi).exec(m[1])[1];
         var f = { name: name, description: desc, sigs: sigs };
         return f;
      }
      return null;
   },


   processFile: function (file) {
      var self = this;

      // Get the file in a buffer
      fs.readFile(file, function(err, data) {
         var buf = data.toString('binary');

         var functions = [];

         // Get all long comment ( /** )
         var rgx = new RegExp("/\\*\\*\n([a-zA-Z0-9 -_\n\t]*)\\*/\n(.*)\n", "gi");
         while (m = rgx.exec(buf)) {
            info = self.extractInfos(m);
            if (info) {
               functions.push(info);
            }
         }

         self.files[file] = { functions: functions };

         self.fileLoaded();
      });
   },


   sortFunctions: function (fun1, fun2) {
      var name1 = fun1.name.toLowerCase();
      var name2 = fun2.name.toLowerCase();
      if      (name1 < name2) { return -1; }
      else if (name1 > name2) { return 1;  }
      else                    { return 0;  }
   },


   exportHtml: function() {
      for (var fileName in this.files) {
         var file = this.files[fileName];
         file.functions.sort(this.sortFunctions);
         console.log(fileName, file.functions.length);

         var html = '<!DOCTYPE html>\n' +
                    '<html>\n' +
                    '<head>\n' +
                    '   <title></title>\n' +
                    '   <link rel="stylesheet" href="css/reset.css" type="text/css" media="screen" charset="utf-8" />\n' +
                    '   <link rel="stylesheet" href="css/style.css" type="text/css" media="screen" charset="utf-8" />\n' +
                    //'   <script src="js/scripts.js" type="text/javascript"></script>' +
                    '</head>\n' +
                    '<body>\n' +
                    '\n' +
                    '<div class="menu" id="menu">\n' +
                    '   <h1>Files</h1>\n' +
                    '   <ul>\n';
         for (var f in this.files) {
            html += '      <li><a href="'+f+'.html">'+f+'</a></li>\n';
         }
         html +=    '   </ul>\n' +
                    '   <h1>Functions</h1>\n' +
                    '   <ul>\n';
         for (var i=0, len=file.functions.length; i<len; i++) {
            html += '      <li><a href="#'+slugify(file.functions[i].name)+'">'+file.functions[i].name+'</a></li>\n';
         }
         html +=    '   </ul>\n'
         html +=    '</div>\n' +
                    '<div id="page">\n' +
                    '   <div class="content">\n';

         for (var i=0, len=file.functions.length; i<len; i++) {
            var fn = file.functions[i];
            if (fn.sigs.length > 0) {
               html += '<h3><a name="'+slugify(fn.name)+'">'+fn.name+'</a></h3>\n';
               html += '<span class="signature">\n';
               for (var s=0, len2=fn.sigs.length; s<len2; s++) {
                  var sig = fn.sigs[s];
                  html += '<span class="name">'+fn.name+'</span> ( ';
                  for (var p=0, len3=sig.params.length; p<len3; p++) {
                     var param = sig.params[p];
                     html += '<span class="param">'+param.name+'</span>:<span class="type">'+param.type+'</span>, ';
                  }
                  html = html.substr(0, html.length-2);
                  html += ' ) : <span class="param">'+sig.ret.name+'</span>:<span class="type">'+sig.ret.type+'</span><br />';
               }
               html = html.substr(0, html.length-6);
               html += '</span>\n';
               html += '<p>'+fn.description+'</p>';
            }
         }
         html +=    '   </div>\n' +
                    '</div>\n' +
                    '\n' +
                    '</body>\n'
                    '</html>';
         fs.writeFile('doc/'+fileName+'.html', html);

      }

   }


};


var files = ['sockets.js', 'database_operations.js'];
DocGen.init(files);
DocGen.start();
  
})();
