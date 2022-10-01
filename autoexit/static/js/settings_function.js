function save_settings(key,value){

	$.ajax({
		url:'save_settings_request',
		type:'POST',
		data:{'key':key,'value': value},
		dataType:'json',
		success: function(data){
			Swal.fire({
				icon:'success',
				title: 'Settings Saved',
				toast: true,
				timer: 1000,
				timerProgressBar: true,
			})
  
		}
	})
}

function ws_scan_input(){
	
  var ws = new WebSocket("ws://127.0.0.1:5678/");
  ws.onmessage = function (event){
  	var wsvalue=parseInt(event.data);
    w3.displayObject("gpio_value", { "gpio_value": wsvalue });
    w3.show('#gpio_value');
    
  }
 
       
}


function save_settings_IO() {
loop_car=document.getElementById('txtCarLoop').value;
loop_motor=document.getElementById('txtMotorLoop').value;
button_car=document.getElementById('txtCarButton').value;
button_motor =document.getElementById('txtMotorButton').value;
help_button=document.getElementById('txtHelpButton').value;
help_car=document.getElementById('txtCarHelpButton').value;
help_motor=document.getElementById('txtMotorHelpButton').value;
vehicle_in_front =document.getElementById('txtVehicleInFront').value;
barrier_pin=document.getElementById('txtOutput').value;

	console.log('save_settings_IO')
	save_settings('loop_car',loop_car);
	save_settings('loop_motor',loop_motor);
	save_settings('button_car',button_car);
	save_settings('button_motor',button_motor);
	save_settings('help_button',help_button);
	save_settings('help_car',help_car);
	save_settings('help_motor',help_motor);
	save_settings('vehicle_in_front',vehicle_in_front);
	save_settings('barrier_pin',barrier_pin);
}




function save_settings_checkbox(checkbox_id,key){

	cb=document.getElementById(checkbox_id);
	if (cb.checked==true){
		save_settings(key,true);

	} else{
		save_settings(key,false);

	}
}

function save_settings_sysimages(){
	vehicle_view=document.getElementById('txtVehicleFrontViewFolder').value;
	driver_view=document.getElementById('txtDriverViewFolder').value;
	lpr=document.getElementById('txtLPRFolder').value;
	save_settings('vehicle_view',vehicle_view);
	save_settings('driver_view',driver_view);
	save_settings('lpr',lpr);

}

function verifylogin(){
	username=document.getElementById('txtusername').value;
	password=document.getElementById('txtpassword').value;


	$.ajax({
		url:'verify_login',
		type:'POST',
		data:{'username':username,'password':password},
		dataType:'json',
		success:function(result){console.log(username);console.log(password);}
	})
}



function scan_value(){
	$("#gpio_value").load("scan_gpio/");


}

function start_scan_value(){
	Swal.fire({
		icon:'info',
		title:'Scanning input pins...',
		toast: true,
		timer: 1000,
		timerProgressBar: true,

	})
	sc= setInterval(scan_value, 300);
	w3.show('#btnStop');
	w3.hide('#btnScan');
	ws_scan_input();


}

function stop_scan_value(){
	w3.show('#btnScan');
	w3.hide('#btnStop');
	w3.hide('#gpio_value');
}


function test_trigger(pin){
	Swal.fire({
				icon:'info',
				title: 'Output Pin ' + pin + '\nTrigger Testing...' ,
				toast: true,
				timer: 1000,
				timerProgressBar: true,
			})
	ws_trigger();
}




function ValidateIPaddress(inputText){
	
	var ipformat = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
	if (inputText.match(ipformat))
		{return true;}
	else
		{
			
			return false;
		}
}


function save_ip_front(){
	iptextbox=document.getElementById('txtFrontCam').value;
	FrontChannel=document.getElementById('txtFrontChannel').value;
	if (ValidateIPaddress(iptextbox)==true)
	{save_settings('cam_front',iptextbox);save_settings('channel_front',FrontChannel);}
	else
	{
		Swal.fire({
				icon: 'warning',
				title: 'Invalid IP Address',
				toast: true,
				
			});

	}
}

function save_ip_rear(){
	iptextbox=document.getElementById('txtRearCam').value;
	RearChannel=document.getElementById('txtRearChannel').value;
	if (ValidateIPaddress(iptextbox)==true)
	{save_settings('cam_rear',iptextbox);save_settings('channel_rear',RearChannel);}
	else
	{
		Swal.fire({
				icon: 'warning',
				title: 'Invalid IP Address',
				toast: true,
			
			});

	}
}

function save_ip_face(){
	iptextbox=document.getElementById('txtFaceCam').value;
	FaceChannel=document.getElementById('txtFaceChannel').value;
	if (ValidateIPaddress(iptextbox)==true)
	{save_settings('cam_face',iptextbox);save_settings('channel_face',FaceChannel);}
	else
	{
		Swal.fire({
				icon: 'warning',
				title: 'Invalid IP Address',
				toast: true,
				
			});

	}
}



function save_camcred(){
	cam_username=document.getElementById('txtCamUsername').value;
	cam_password=document.getElementById('txtCamPassword').value;
	save_settings('cam_username',cam_username);
	save_settings('cam_password', cam_password);
}






function toggle_password(){
    var x = document.getElementById("txtCamPassword");

    
  if (x.type === "password") {
    x.type = "text";
    w3.hide("#i_show");
    w3.show("#i_hide");

  } else {
    x.type = "password";
      w3.show("#i_show");
    w3.hide("#i_hide");
  }

  }


  function ReadFile(){
  	const fs=require('fs');
  	let directory ="/srv/share/qrimage";
  	let dirBuf=Buffer.from(directory);
  	fs.readdir(dirBuf,(err,files)=>{
  		if (err){
  			console.log(err.message);
  		}else{
  		console.log(files);
  	}
  })
  }