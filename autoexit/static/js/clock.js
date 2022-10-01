

Number.prototype.pad = function(n) {
  for (var r = this.toString(); r.length < n; r = 0 + r);
  return r;
};

function updateClock() {
  var now = new Date();
  var milli = now.getMilliseconds(),
    sec = now.getSeconds(),
    min = now.getMinutes(),
    hou = now.getHours(),
    mo = now.getMonth(),
    dy = now.getDate(),
    yr = now.getFullYear();
    var ampm = ( hou < 12 ) ? "AM" : "PM";
    hou =(hou > 12) ? hou - 12 : hou;
  var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var tags = ["mon", "d", "y", "h", "m", "s", "t"],
    corr = [months[mo], dy, yr, hou.pad(2), min.pad(2), sec.pad(2), ampm];

/*  for (var i = 0; i < tags.length; i++)
    document.getElementById(tags[i]).firstChild.nodeValue = corr[i];*/
    document.getElementById('clock').innerHTML = months[mo] + " " + dy.pad(2) + ", " + yr + " "+ hou.pad(2) + " : " + min.pad(2) + " : " + sec.pad(2) + " " + ampm
}

function initClock() {
  updateClock();
  window.setInterval("updateClock()", 1000);
}



