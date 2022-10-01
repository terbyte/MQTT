var status_scanner=0;
var status_trigger=0;
var status_reader=0;


function startup_checks(){
	sendF11();
	start_count();
	
	
}


function check_reader(){
	$.ajax({
    url: "connected_qrreader",
    type: "GET",
    dataType: "json",
    success: function (result) { 
    	status_reader=result;
    	
    	if(result!=0){resultmsg="Refreshing system. Please wait...";w3.hide('#txtNoreaderH1');w3.hide('#txtNoreaderH2');	w3.displayObject("txtReader",{"txtReader":resultmsg});
   	 	w3.show('#txtReader');}
     
    	
    }

  })
}

function start_count(){
	mx=setInterval(counter_status,1000);
}

function stop_count(){
	clearInterval(mx);
}

function counter_status(){
	if ( status_reader==1 ){
		stop_count();
		window.location='home';
	}

	if (status_reader===0){check_reader();}
	
	
}


function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

function sendF11() {
  if (!window.screenTop && !window.screenY) { console.log('Browser is in fullscreen already'); return; }
  $.ajax({
    url: "sendF11",
    type: "GET",
    dataType: "json",
    success: function (data) { console.log("sendF11") }
  })
}
