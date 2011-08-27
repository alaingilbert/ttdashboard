/*
Copyright (c) 2010, ALAIN GILBERT.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. All advertising materials mentioning features or use of this software
   must display the following acknowledgement:
   This product includes software developed by ALAIN GILBERT.
4. Neither the name of the ALAIN GILBERT nor the
   names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY ALAIN GILBERT ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL ALAIN GILBERT BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
window.Gauge=function(a,c){var b=c!==void 0?c:{};this.elemId=a;this.needleColor=b.needleColor!==void 0?b.needleColor:"black";this.gaugeColor=b.gaugeColor!==void 0?b.gaugeColor:"lightblue";this.min=0;this.max=100;this.value=0;this.callback=this.newValue=this.fromValue=this.interval=null;this.bindElems=[];this.canvas=document.getElementById(this.elemId);this.width=this.canvas.width;this.height=this.canvas.height;this.ctx=this.canvas.getContext("2d");this.paint()};Gauge.prototype.bind=function(a){this.bindElems.push(document.getElementById(a))};
Gauge.prototype.setValue=function(a,c){if(this.value!=a){window.clearInterval(this.interval);this.fromValue=this.value;this.newValue=a;this.startTime=(new Date).getTime();this.callback=c;var b=this;this.interval=window.setInterval(function(){b.update();b.paint()},1E3/60)}};
Gauge.prototype.update=function(){var a=this.formulas["<>"](((new Date).getTime()-this.startTime)/2E3);if((new Date).getTime()-this.startTime<=2E3){this.value=(this.newValue-this.fromValue)/2E3*a*2E3+this.fromValue;for(a=0;a<this.bindElems.length;a++)this.bindElems[a].innerHTML=Math.floor(this.value)}else{this.value=this.newValue;for(a=0;a<this.bindElems.length;a++)this.bindElems[a].innerHTML=this.value;window.clearInterval(this.interval);this.callback&&this.callback()}};
Gauge.prototype.paint=function(){this.ctx.clearRect(0,0,this.width,this.height);this.ctx.save();this.ctx.beginPath();this.ctx.translate(this.width/2,this.height);var a=Math.atan(this.height/2/(this.width/2));this.ctx.arc(0,0,this.width/2,-Math.PI+a,-a);this.ctx.arc(0,0,this.width/2-45,-a,-Math.PI+a,!0);this.ctx.closePath();this.ctx.fillStyle=this.gaugeColor;this.ctx.fill();this.ctx.restore();var c=-Math.PI/2+a,a=-Math.PI/2+a+(Math.PI-2*a)-c,b=this.value/this.max;this.ctx.save();this.ctx.translate(this.width/
2,this.height);this.ctx.rotate(b*a+c);this.ctx.beginPath();this.ctx.moveTo(0,0);this.ctx.lineTo(-5,-5);this.ctx.lineTo(0,-this.height);this.ctx.lineTo(5,-5);this.ctx.closePath();this.ctx.fillStyle=this.needleColor;this.ctx.fill();this.ctx.restore()};
Gauge.prototype.formulas={linear:function(a){return a},"<":function(a){return Math.pow(a,3)},">":function(a){return Math.pow(a-1,3)+1},"<>":function(a){a*=2;if(a<1)return Math.pow(a,3)/2;a-=2;return(Math.pow(a,3)+2)/2},backIn:function(a){return a*a*(2.70158*a-1.70158)},backOut:function(a){a-=1;return a*a*(2.70158*a+1.70158)+1},elastic:function(a){return a==0||a==1?a:Math.pow(2,-10*a)*Math.sin((a-0.075)*2*Math.PI/0.3)+1},bounce:function(a){a<1/2.75?a*=7.5625*a:a<2/2.75?(a-=1.5/2.75,a=7.5625*a*a+0.75):
a<2.5/2.75?(a-=2.25/2.75,a=7.5625*a*a+0.9375):(a-=2.625/2.75,a=7.5625*a*a+0.984375);return a}};
