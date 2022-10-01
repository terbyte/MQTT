var status_scanner=0;
var status_trigger=0;
var status_reader=0;


function startup_checks(){
	sendF11();
	start_count();
	
	
}




function check_scanner(){
	var ws_scan = new WebSocket("ws://127.0.0.1:5678/");
	
	ws_scan.onopen=function(e){
		w3.displayObject("txtScanner", { "txtScanner": " Scanner Websocket Connected " });
  		w3.show('#txtScanner');
  		
  		status_scanner=1;
	}

	ws_scan.onerror=function(error){
		
		w3.displayObject("txtScanner", { "txtScanner": "Scanner Websocket Error" });
  		w3.show('#txtScanner');
  		status_scanner=0;
	}	


	
}


function check_trigger(){
	var ws_trigger =new WebSocket("ws://127.0.0.1:5679/");
	ws_trigger.onopen=function(e){
		w3.displayObject("txtTrigger", { "txtTrigger": " Trigger Websocket Connected " });
  		w3.show('#txtTrigger');
		
		
		status_trigger=1;
		
	}

	ws_trigger.onerror=function(error){
		w3.displayObject("txtTrigger", { "txtTrigger": "Trigger Websocket Error" });
  		w3.show('#txtTrigger');
  		status_trigger=0;
	}

}
function check_reader(){
	var ws_reader=new WebSocket("ws://127.0.0.1:5680/");
	ws_reader.onopen=function(e){		
  ws_reader.send("init_crt310");
	}
	ws_reader.onerror=function(error){
		w3.displayObject("txtReader", { "txtReader": "Reader Websocket Error" });
  		w3.show('#txtReader');
  		status_reader=0;
	}

	 ws_reader.onmessage = function (event){
	 	if (event.data==='Initialize : OK'){
	 			
	 			status_reader=1;
	 	}
	 	else {
	 			
	 		status_reader=0;
	 	}
	 w3.displayObject("txtReader",{"txtReader": event.data});
	 			w3.show('#txtReader');
	 }

}

function start_count(){
	mx=setInterval(counter_status,1000);
}

function stop_count(){
	clearInterval(mx);
}

function counter_status(){
	if ( status_reader==1 && status_scanner==1 && status_trigger==1){
		stop_count();
		window.location='home';
	}

	if (status_reader===0){check_reader();}
	if (status_scanner===0){check_scanner();}
	if (status_trigger===0){check_trigger();}
	
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
