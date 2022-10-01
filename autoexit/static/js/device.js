var CardStacker=0;
var AlreadyMoved=0;
var AlreadyOut=0;
var AlreadyTriggered=0;
var Data_to_Encrypt="";
var siteID;
var zoneID;
var vehicleID=1;
var time_in=""
var timestamp=""
var vehicle_type ="CAR";
var card_code;
var plate_number="-";
var timein_write="";

var loop_car; //=4;
var loop_motor ;//=8;
var button_car ;//=132;
var button_motor;//=136;
var default_input=0;
var mqtt_msg="";

var lack_alert;
var empty_alert;
var hascard=0;
var already_seeking=0;
var seeker;
var already_stopped=0;
var counter_seek;
var system_ok=0;
var checker;
var hascrt=0;

var hasvehicle=0;
var noloop;

var loopvalue=0;

function ws_scan(){
  var ws = new WebSocket("ws://127.0.0.1:5678/");
  ws.onmessage = function (event){
    var wsvalue=parseInt(event.data);loopvalue=wsvalue
    if (noloop=='true'){
      if (wsvalue==default_input){car_detected();}
    }
    else{
      if (wsvalue==loop_car) {car_detected();};
      if (wsvalue==loop_motor){motor_detected();};          
      if (wsvalue==default_input){reset_default();};
    }
  }
  ws.onerror=function(event){show_unavailable();}       
}

function ws_trigger(){
  var ws = new WebSocket("ws://127.0.0.1:5679/");
  ws.onopen=function(){ws.send("trigger now");}
  ws.onerror=function(event){show_unavailable();}
}


function ws_init_crt310(){
  var ws = new WebSocket("ws://127.0.0.1:5680");
  ws.onopen=function(){ws.send("init_crt310");}
  ws.onmessage =function(event){
    var result=event.data;
    alert(result);
  }
}


function ws_release_card(){
  var ws = new WebSocket("ws://127.0.0.1:5680");
  ws.onopen=function(){ws.send("release_card");}
  ws.onmessage =function(event){
    var result=event.data;
    // alert(result);
  }
}

function ws_accept_card(){
  var ws = new WebSocket("ws://127.0.0.1:5680");
  ws.onopen=function(){ws.send("accept_card");}
  ws.onmessage =function(event){
    var result=event.data;
    // alert(result);
  }
}


function ws_seek_card(){
  var ws = new WebSocket("ws://127.0.0.1:5680");
  ws.onopen=function(){ws.send("seek_card");}
  ws.onmessage =function(event){
    var result=event.data;
    
    if (result==='LIMITED' || result==='INVALID'){

      if (loopvalue!=default_input){ws_seek_card();}
    }


    if (result==='VERIFIED')
      {
        show_card_verified();
        ws_trigger();//ws_accept_card();
        snapshot();faceshot();
     
        if (noloop==='true'){setTimeout(car_detected, 5000);}
        
      }

      if (result==='GP'){
        show_GP();
        ws_trigger();//ws_accept_card();
        snapshot();faceshot();
           
        if (noloop==='true'){setTimeout(car_detected, 5000);}  

      }
      if (result==='NOTVERIFIED'){show_card_notverified();ws_release_card();}
      if (result==='INVALID'){show_card_invalid();ws_release_card();}
      if (result==='USED'){show_ticket_used();ws_release_card();}
      if (result.includes('EXCEEDED')){
        rs=result.split(",")
        excess=rs[1]
        
        if (excess==="1"){excess=" "+rs[1]+ " minute"}
        else {excess=" "+rs[1]+ " minutes"}
        timepaid=" " +rs[2]
        
        w3.displayObject("txt_excess", { "txt_excess": excess,"txt_paid":timepaid});
        
        show_card_exceed();ws_release_card();}
  }
}


function check_reader(){
  $.ajax({
    url: "crt_check",
    type: "GET",
    dataType: "json",
    success: function (result){
      if (result!="CRT-OK"){     
        Swal.fire({
          icon:'warning',
          title: 'No QR Reader Detected',
          toast: true,
          timer: 2500,
          timerProgressBar: true,})
        show_noreader();
      }
    }
  })
}


function delete_from_scanned(){
  $.ajax({
    url:"delete_from_scanned",
    type:"GET",
    dataType:"json",
    success:function(result){}
  })
}

function delete_from_timein(){
  $.ajax({
    url:"delete_from_timein",
    type:"GET",
    dataType:"json",
    success:function(result){}
  })
}

function show_unavailable(){
  window.location='machine_unavailable';
}
function show_noreader(){
  window.location='noreader';
}

function car_detected(){
  show_card_insert();
  ws_seek_card();
  // already_stopped=0;
  // if (already_seeking==0){
  //   show_card_insert();
  //   vehicleID=2;
  //   start_seek();
  //   already_seeking=1;
  // }
 
}  


function motor_detected(){
  show_card_insert();
   ws_seek_card();
  // already_stopped=0;  
  // if (already_seeking==0){
  //   show_card_insert();
  //   vehicleID=1;
  //   start_seek();
  //   already_seeking=1;
  // }
}  


function sendF11(){
 if (!window.screenTop && !window.screenY) {console.log('Browser is in fullscreen already');return;}
  $.ajax({
    url: "sendF11",
    type: "GET",
    dataType: "json",
    success: function (data){console.log("sendF11")}
  })
}






function reset_default(){
  show_ads();
  hasvehicle=0; 

}  

function settings_toJS(){
     $.ajax({
      url: "settings_toJS",
      type: "GET",
      dataType: "json",
      success: function(data){

      loop_car=data.loop_car;
      loop_motor=data.loop_motor;
      button_car =data.button_car;
      button_motor=data.button_motor;

      siteID=data.siteID;
      zoneID=data.zoneID;

      exit_GP=data.exit_GP;

      noloop=data.noloop;


      }

    })

  }  


function get_datetime_now(){
  var now = new Date();
  var milli = now.getMilliseconds(),
    sec = now.getSeconds(),
    min = now.getMinutes(),
    hou = now.getHours(),
    hr=hou
    mo = now.getMonth(),
    dy = now.getDate(),
    yr = now.getFullYear();
    var ampm = ( hou < 12 ) ? "AM" : "PM";
    hou =(hou > 12) ? hou - 12 : hou;
  var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var tags = ["mon", "d", "y", "h", "m", "s", "t"],
    corr = [months[mo], dy, yr, hou.pad(2), min.pad(2), sec.pad(2), ampm];
    timestamp=yr+(mo+1).pad(2)+dy.pad(2)+hr.pad(2)+min.pad(2)+sec.pad(2);
    timein_write=yr+"-"+(mo+1).pad(2)+"-"+dy.pad(2)+" "+ hr.pad(2)+":" + min.pad(2)+":"+sec.pad(2)
    console.log("Timestamp: " + timestamp);


    return months[mo] + " " + dy.pad(2) + ", " + yr + " "+ hou.pad(2) + " : " + min.pad(2) + " : " + sec.pad(2) + " " + ampm
}








function OpenBarrier(){
    $.ajax({
      url: "open_barrier",
      type: "GET",
      dataType: "json",
      success: function(data){console.log("Opening Barrier...");}
    })
}  

function snapshot(){
  $.ajax({
    url: "snapshot",
    type: "GET",   
    dataType: "json",    
    success: function(response){}
  })
}

function faceshot(){  
  $.ajax({
    url: "faceshot",
    type: "GET",   
    dataType: "json",
    success: function(response){}
  })
}




function get_platenumber(){
  $.ajax({
    url: "get_plate/",
    type: "POST",
    dataType: "json",
    success: function(response){plate_number=response;console.log(plate_number);}

  })

}

function get_platenumber_rear(){
  $.ajax({
    url: "get_plate_rear/",
    type: "POST",
    dataType: "json",
    success: function(response){plate_number=response; console.log(plate_number);}

  })

}


 function mqtt_logs(){ 
    $.ajax({
    url: "mqtt_logs",
    type: "POST",
    data: {"mqtt_msg":mqtt_msg},
    dataType: "json",
    success: function(result){
      console.log("mqtt_logs: "  +result);
    }
  })
 }


 function machine_status(status_msg){ 
    $.ajax({
    url: "machine_status",
    type: "POST",
    data: {"mqtt_msg":status_msg},
    dataType: "json",
    success: function(result){
      console.log("machine_status: "  +result);
    }
  })
 }

function MS(){
  machine_status("TESTING MACHINE STATUS");
}

function restart_machine(){
  Swal.fire({
    toast: true,
    title: 'Restart Machine?',
    text: "The machine will restart immediately upon confirmation.",
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#008080',
    cancelButtonColor: '#aaa',
    confirmButtonText: 'Yes, restart it.',
    reverseButtons: false,
    showCloseButton: true,
  }).then((result) => {
  if (result.isConfirmed){
        $.ajax({
        url: "restart_machine",
        type:"GET",
        dataType:"json",
        success:function(result){console.log(result);}
      })
    }
  })
  
}

function shutdown_machine(){
   Swal.fire({
    toast: true,
    title: 'Shutdown Machine?',
    text: "The machine will shutdown immediately upon confirmation.",
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#008080',
    cancelButtonColor: '#aaa',
    confirmButtonText: 'Yes, shut it down.',
    reverseButtons: false,
    showCloseButton: true,
  }).then((result) => {
  if (result.isConfirmed){
        $.ajax({
        url: "shutdown_machine",
        type:"GET",
        dataType:"json",
        success:function(result){console.log(result);}
      })
    }
  })
}
 


function toggleFullScreen() {
  if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }
}


document.addEventListener("keypress",function(e){
  if (e.keyCode===13){
    if (hasvehicle==1){read_qr();document.getElementById('txtQR').value = '';focus_qrbox();}
    else{show_novehicle()};
  }
},false);

document.addEventListener("keypress",function(e){
  if (e.keyCode===97){
    snapshot();faceshot();
  }
},false);

 
 
function read_qr(){
  qrstr=document.getElementById('txtQR').value;
  $.ajax({
    url: "read_qr",
    type:"POST",
    data: {'qrstr':qrstr},
    dataType:"json",
    success:function(result){  console.log(result); 

      if (result==='VERIFIED')
      {
        show_card_verified();
        ws_trigger();
        snapshot();faceshot();
        delete_from_timein();
        delete_from_scanned();
        if (noloop==='true'){setTimeout(car_detected, 5000);}
        
      }

      if (result==='GP'){
        show_GP();
        ws_trigger();
        snapshot();faceshot();
        delete_from_timein();
        delete_from_scanned();    
        if (noloop==='true'){setTimeout(car_detected, 5000);}  

      }
      if (result==='NOTVERIFIED'){show_card_notverified();}
      if (result==='INVALID'){show_card_invalid();}
      if (result==='USED'){show_ticket_used();}
      if (result.includes('EXCEEDED')){
        rs=result.split(",")
        excess=rs[1]
        
        if (excess==="1"){excess=" "+rs[1]+ " minute"}
        else {excess=" "+rs[1]+ " minutes"}
        timepaid=" " +rs[2]
        
        w3.displayObject("txt_excess", { "txt_excess": excess,"txt_paid":timepaid});
        
        show_card_exceed();}
    }
  })
}

function show_ticket_used(){
  w3.show('#used_ticket');
  w3.hide('#machine_unavailable');
  w3.hide('#txt_excess');
  w3.hide('#card_insert');
  w3.hide('#card_verified');
  w3.hide('#card_notverified');
  w3.hide('#card_invalid');
  w3.hide('#card_exceed');
  w3.hide('#slider');
  w3.hide('#card_errors4');
  w3.hide('#card_errors3');
  w3.hide('#novehicle');
  w3.hide('#insert_ticket');
  w3.hide('#card_gp');
  if (noloop==='true'){setTimeout(car_detected, 5000);}

}

function show_machine_unavailable() {
  w3.show('#machine_unavailable');
  w3.hide('#txt_excess');
  w3.hide('#card_insert');
  w3.hide('#card_verified');
  w3.hide('#card_notverified');
  w3.hide('#card_invalid');
  w3.hide('#card_exceed');
  w3.hide('#slider');
  w3.hide('#card_errors4');
  w3.hide('#card_errors3');
  w3.hide('#novehicle');
  w3.hide('#insert_ticket');
  w3.hide('#used_ticket');
  w3.hide('#card_gp');

}

function show_novehicle() {
  w3.show('#novehicle');
  w3.hide('#machine_unavailable');
  w3.hide('#txt_excess');
  w3.hide('#card_insert');
  w3.hide('#card_verified');
  w3.hide('#card_notverified');
  w3.hide('#card_invalid');
  w3.hide('#card_exceed');
  w3.hide('#slider');
  w3.hide('#card_errors4');
  w3.hide('#card_errors3');
  w3.hide('#insert_ticket');
  w3.hide('#used_ticket');
  w3.hide('#card_gp');
  
   Swal.fire({
          icon:'warning',
          title: 'No Vehicle Detected',
          toast: true,
          timer: 2500,
          timerProgressBar: true,})


}



function show_card_insert() {
  w3.hide('#txt_excess');
  w3.show('#card_insert');
  w3.hide('#card_verified');
  w3.hide('#card_notverified');
  w3.hide('#card_invalid');
  w3.hide('#card_exceed');
  w3.hide('#slider');
  w3.hide('#card_errors4');
  w3.hide('#card_errors3');
  w3.hide('#machine_unavailable');
  w3.hide('#novehicle');
  w3.hide('#insert_ticket');
  w3.hide('#used_ticket');
  w3.hide('#card_gp');
   if (noloop==="false"){document.getElementById("sound_card_insert").play();} 
}

function show_GP(){
  w3.show('#card_gp');
  w3.hide('#txt_excess');
  w3.hide('#card_insert');
  w3.hide('#card_verified');
  w3.hide('#card_notverified');
  w3.hide('#card_invalid');
  w3.hide('#card_exceed');
  w3.hide('#slider');
  w3.hide('#card_errors4');
  w3.hide('#card_errors3');
  w3.hide('#machine_unavailable');
  w3.hide('#novehicle');
  w3.hide('#insert_ticket');
  w3.hide('#used_ticket');
  document.getElementById("sound_card_gp").play(); 

}

function show_card_verified() {
  w3.hide('#txt_excess');
  w3.show('#card_verified');
  w3.hide('#card_insert');
  w3.hide('#card_notverified');
  w3.hide('#card_invalid');
  w3.hide('#card_exceed');
  w3.hide('#slider');
  w3.hide('#card_errors4');
  w3.hide('#card_errors3');
  w3.hide('#machine_unavailable');
  w3.hide('#novehicle');
  w3.hide('#insert_ticket');
  w3.hide('#used_ticket');
  w3.hide('#card_gp');
   document.getElementById("sound_card_verified").play(); 
}

function show_card_notverified() {
  w3.hide('#txt_excess');
  w3.show('#card_notverified');
  w3.hide('#card_insert');
  w3.hide('#card_verified');
  w3.hide('#card_invalid');
  w3.hide('#card_exceed');
  w3.hide('#slider');
  w3.hide('#card_errors4');
  w3.hide('#card_errors3');
  w3.hide('#machine_unavailable');
  w3.hide('#novehicle');
  w3.hide('#insert_ticket');
  w3.hide('#used_ticket');
  w3.hide('#card_gp');
  document.getElementById("sound_card_notverified").play(); 
  if (noloop==='true'){setTimeout(car_detected, 5000);}
}

function show_card_invalid() {
  w3.hide('#txt_excess');
  w3.show('#card_invalid');
  w3.hide('#card_insert');
  w3.hide('#card_verified');
  w3.hide('#card_notverified');  
  w3.hide('#card_exceed');
  w3.hide('#slider');
  w3.hide('#card_errors4');
  w3.hide('#card_errors3');
  w3.hide('#machine_unavailable');
  w3.hide('#novehicle');
  w3.hide('#insert_ticket');
  w3.hide('#used_ticket');
  w3.hide('#card_gp');
   document.getElementById("sound_card_invalid").play(); 
   if (noloop==='true'){setTimeout(car_detected, 5000);}
}

function show_card_exceed() {
  w3.show('#txt_excess');
  w3.show('#card_exceed');
  w3.hide('#card_insert');
  w3.hide('#card_verified');
  w3.hide('#card_notverified'); 
  w3.hide('#card_invalid'); 
  w3.hide('#slider');
  w3.hide('#card_errors4');
  w3.hide('#card_errors3');
  w3.hide('#machine_unavailable');
  w3.hide('#novehicle');
  w3.hide('#insert_ticket');
  w3.hide('#used_ticket');
  w3.hide('#card_gp');
  document.getElementById("sound_card_exceed").play();
  if (noloop==='true'){setTimeout(car_detected, 5000);}
}

function show_card_errors3() {
  w3.show('#card_errors3');
  w3.hide('#card_errors4');
  w3.hide('#txt_excess');
  w3.hide('#card_exceed');
  w3.hide('#card_insert');
  w3.hide('#card_verified');
  w3.hide('#card_notverified'); 
  w3.hide('#card_invalid');
  w3.hide('#machine_unavailable'); 
  w3.hide('#slider');
  w3.hide('#novehicle');
  w3.hide('#insert_ticket');
  w3.hide('#used_ticket');
  w3.hide('#card_gp');
  
}
function show_card_errors4() {
  w3.show('#card_errors4');
  w3.hide('#card_errors3');
  w3.hide('#txt_excess');
  w3.hide('#card_exceed');
  w3.hide('#card_insert');
  w3.hide('#card_verified');
  w3.hide('#card_notverified'); 
  w3.hide('#card_invalid');
  w3.hide('#machine_unavailable'); 
  w3.hide('#slider');
  w3.hide('#novehicle');
  w3.hide('#insert_ticket');
  w3.hide('#used_ticket');
  w3.hide('#card_gp');
  
}


function show_ads(){
   w3.hide('#txt_excess');
  w3.show('#slider');
  w3.hide('#card_insert');
  w3.hide('#card_verified');
  w3.hide('#card_notverified');
  w3.hide('#card_invalid');
  w3.hide('#card_exceed');
  w3.hide('#card_errors4');
  w3.hide('#card_errors3');
  w3.hide('#machine_unavailable');
  w3.hide('#novehicle');
  w3.hide('#insert_ticket');
  w3.hide('#used_ticket');
  w3.hide('#card_gp');
}



function get_datetime_now(){
  var now = new Date();
  var milli = now.getMilliseconds(),
    sec = now.getSeconds(),
    min = now.getMinutes(),
    hou = now.getHours(),
    hr=hou
    mo = now.getMonth(),
    dy = now.getDate(),
    yr = now.getFullYear();
    var ampm = ( hou < 12 ) ? "AM" : "PM";
    hou =(hou > 12) ? hou - 12 : hou;
  var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var tags = ["mon", "d", "y", "h", "m", "s", "t"],
    corr = [months[mo], dy, yr, hou.pad(2), min.pad(2), sec.pad(2), ampm];
    timestamp=yr+(mo+1).pad(2)+dy.pad(2)+hr.pad(2)+min.pad(2)+sec.pad(2);
    timein_write=yr+"-"+(mo+1).pad(2)+"-"+dy.pad(2)+" "+ hr.pad(2)+":" + min.pad(2)+":"+sec.pad(2)
    console.log("Timestamp: " + timestamp);


    return months[mo] + " " + dy.pad(2) + ", " + yr + " "+ hou.pad(2) + " : " + min.pad(2) + " : " + sec.pad(2) + " " + ampm
}

function play_systemstart() {
  document.getElementById('SystemStart').play();
}
function play_cardverified(){
  document.getElementById('sound_card_verified').play();
}


function focus_qrbox(){
  document.getElementById("txtQR").focus();
}

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}         

// const myTimeout = setTimeout(myGreeting, 5000);

function seek_card(){
  $.ajax({
    url:"seek_card",
    type:"GET",
    dataType:"json",
    success:function(data){ hascard=data; console.log("seek_card:" + hascard); }
  })
}

function start_seek() {
  counter_seek=0;
  seeker=setInterval(seeking,1000);
  function seeking() {
    if (hascard == 1) {
      clearInterval(seeker);
      console.log("Seeking Stopped.");
      vehicle_detected();
      counter_seek=0;
    } else {
      // seek_card();
      if (counter_seek<=9){seek_card();console.log("Seeking..."+counter_seek);counter_seek=counter_seek+1;}
      else {stop_seek();release_card();show_card_invalid();counter_seek=0;already_seeking=0;}
      
      
    }
  }
}

function stop_seek(){
  clearInterval(seeker);
  console.log("Seeking Stopped...");
}


function release_card(){
  $.ajax({
    url:"release_card",
    type:"GET",
    dataType:"json",
    success: function(data){console.log("release_card:"+data)}

  })
}
