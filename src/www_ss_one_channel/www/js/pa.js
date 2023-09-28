function readStatus_lna()
{
	$(":button").attr('disabled',true);
	var radioVal = 2;
	var radio1 = document.getElementById("radio_up_lna");
	var radio2 = document.getElementById("radio_down_lna");
	if(radio1.checked == true)
		radioVal = 1;
	else if(radio2.checked == true)
		radioVal = 0;
		
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:1,
		readid:document.getElementById("select_id_lna").selectedIndex,
		readstream:radioVal,
	},function(data,status){
		if(status == "success"){
			try{
				var obj = JSON.parse(data);
				$("#textbox_decay_lna").val(obj.att);
				$("#textbox_alc_lna").val(obj.alc);
				$("#span_maxGain_lna").text(obj.maxGain+"dBm");
				
				if((obj.status >> 0 & 0x01) == 0x01)
					$("#div_fault_lna").css("background-color","red");
				else 
					$("#div_fault_lna").css("background-color","green");
					
				if((obj.status >> 1 & 0x01) == 0x01)
					$("#div_status_lna").css("background-color","green");
				else 
					$("#div_status_lna").css("background-color","red");
				
				if((obj.status >> 2 & 0x01) == 0x01)
					$("#div_temp_lna").css("background-color","red");
				else 
					$("#div_temp_lna").css("background-color","green");
				
				if((obj.status >> 3 & 0x01) == 0x01)
					$("#div_swr_lna").css("background-color","red");
				else 
					$("#div_swr_lna").css("background-color","green");
				
				if((obj.status >> 4 & 0x01) == 0x01)
					$("#div_power_lna").css("background-color","red");
				else 
					$("#div_power_lna").css("background-color","green");
					
				LogDebug(LogMsgType.Normal,"查询成功");
			}
			catch(e){
				LogDebug(LogMsgType.Normal,data);
			}
		}
		else alert("error");
		$(":button").attr('disabled',false);
	});
}

function writeID_lna()
{
	$(":button").attr('disabled',true);
	var val1 = 2;
	var radio1 = document.getElementById("radio_up_lna");
	var radio2 = document.getElementById("radio_down_lna");
	if(radio1.checked == true)
		val1 = 1;
	else if(radio2.checked == true)
		val1 = 0;
		
	var val2 = 2;
	var radio3 = document.getElementById("radio_writeUp_lna");
	var radio4 = document.getElementById("radio_writeDown_lna");
	if(radio3.checked == true)
		val2 = 1;
	else if(radio4.checked == true)
		val2 = 0;
		
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:2,
		readid:document.getElementById("select_id_lna").selectedIndex,
		readstream:val1,
		writeid:document.getElementById("select_writeid_lna").selectedIndex,
		writestream:val2,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
		$(":button").attr('disabled',false);
	});
}

function writeOnOff_lna()
{
	$(":button").attr('disabled',true);
	var radioVal = 2;
	var radio1 = document.getElementById("radio_up_lna");
	var radio2 = document.getElementById("radio_down_lna");
	if(radio1.checked == true)
		radioVal = 1;
	else if(radio2.checked == true)
		radioVal = 0;
		
	var val = 2;
	if($("#button_onOff_lna").text() == "关闭模块")
		val = 0;
	else if($("#button_onOff_lna").text() == "打开模块")
		val = 1;
		
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:3,
		readid:document.getElementById("select_id_lna").selectedIndex,
		readstream:radioVal,
		onoff:val,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
			if($("#button_onOff_lna").text() == "关闭模块")
				$("#button_onOff_lna").text("打开模块");
			else if($("#button_onOff_lna").text() == "打开模块")
				$("#button_onOff_lna").text("关闭模块");
		}
		else alert("error");
		$(":button").attr('disabled',false);
	});
}

function writeDecay_lna()
{
	$(":button").attr('disabled',true);
	var radioVal = 2;
	var radio1 = document.getElementById("radio_up_lna");
	var radio2 = document.getElementById("radio_down_lna");
	if(radio1.checked == true)
		radioVal = 1;
	else if(radio2.checked == true)
		radioVal = 0;
		
	var val2 = 2;
	var radio3 = document.getElementById("radio_save_lna");
	var radio4 = document.getElementById("radio_noSave_lna");
	if(radio3.checked == true)
		val2 = 0;
	else if(radio4.checked == true)
		val2 = 1;
		
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:4,
		readid:document.getElementById("select_id_lna").selectedIndex,
		readstream:radioVal,
		save:val2,
		step:document.getElementById("select_step_lna").selectedIndex,
		decay:$("#textbox_decay_lna").val(),
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
		$(":button").attr('disabled',false);
	});
}

function writeALC_lna()
{
	$(":button").attr('disabled',true);
	var radioVal = 2;
	var radio1 = document.getElementById("radio_up_lna");
	var radio2 = document.getElementById("radio_down_lna");
	if(radio1.checked == true)
		radioVal = 1;
	else if(radio2.checked == true)
		radioVal = 0;
		
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:5,
		readid:document.getElementById("select_id_lna").selectedIndex,
		readstream:radioVal,
		alc:$("#textbox_alc_lna").val(),
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
		$(":button").attr('disabled',false);
	});
}

function readVersion_lna()
{
	$(":button").attr('disabled',true);
	var radioVal = 2;
	var radio1 = document.getElementById("radio_up_lna");
	var radio2 = document.getElementById("radio_down_lna");
	if(radio1.checked == true)
		radioVal = 1;
	else if(radio2.checked == true)
		radioVal = 0;
		
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:6,
		readid:document.getElementById("select_id_lna").selectedIndex,
		readstream:radioVal,
	},function(data,status){
		if(status == "success"){
			try{
				var obj = JSON.parse(data);
				$("#span_version_lna").text(obj.version);
				LogDebug(LogMsgType.Normal,"软件版本："+obj.version);
			}
			catch(e){
				LogDebug(LogMsgType.Normal,data);
			}
		}
		else alert("error");
		$(":button").attr('disabled',false);
	});
}

function readStatus_pa()
{
	$(":button").attr('disabled',true);
	var radioVal = 2;
	var radio1 = document.getElementById("radio_up_pa");
	var radio2 = document.getElementById("radio_down_pa");
	if(radio1.checked == true)
		radioVal = 1;
	else if(radio2.checked == true)
		radioVal = 0;
		
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:7,
		readid:document.getElementById("select_id_pa").selectedIndex,
		readstream:radioVal,
	},function(data,status){
		if(status == "success"){
			try{
				var obj = JSON.parse(data);
				if((obj.status >> 0 & 0x01) == 0x01)
					$("#div_status_pa").css("background-color","green");
				else 
					$("#div_status_pa").css("background-color","red");
					
				if((obj.status >> 1 & 0x01) == 0x01)
					$("#div_power_pa").css("background-color","red");
				else 
					$("#div_power_pa").css("background-color","green");
				
				if((obj.status >> 2 & 0x01) == 0x01)
					$("#div_temp_pa").css("background-color","red");
				else 
					$("#div_temp_pa").css("background-color","green");
				
				if((obj.status >> 3 & 0x01) == 0x01)
					$("#div_swr_pa").css("background-color","red");
				else 
					$("#div_swr_pa").css("background-color","green");
				
				if((obj.status >> 4 & 0x01) == 0x01)
					$("#div_fault_pa").css("background-color","red");
				else 
					$("#div_fault_pa").css("background-color","green");
					
				$("#span_temp_pa").text(obj.temp+"℃");
				$("#textbox_alc_pa").val(obj.alc);
				$("#textbox_decay_pa").val(obj.att);
				$("#span_swr_pa").text(obj.swr.toFixed(1));
				$("#span_forward_power_pa").text(obj.forward_power);
				$("#textbox_offset_pa_forward").val(obj.offset_forward);
				$("#textbox_offset_pa_input").val(obj.offset_input);
				LogDebug(LogMsgType.Normal,"查询成功");
			}
			catch(e){
				LogDebug(LogMsgType.Normal,data);
			}
		}
		else alert("error");
		$(":button").attr('disabled',false);
	});
}

function writeID_pa()
{
	$(":button").attr('disabled',true);
	var val1 = 2;
	var radio1 = document.getElementById("radio_up_pa");
	var radio2 = document.getElementById("radio_down_pa");
	if(radio1.checked == true)
		val1 = 1;
	else if(radio2.checked == true)
		val1 = 0;
		
	var val2 = 2;
	var radio3 = document.getElementById("radio_writeUp_pa");
	var radio4 = document.getElementById("radio_writeDown_pa");
	if(radio3.checked == true)
		val2 = 1;
	else if(radio4.checked == true)
		val2 = 0;
		
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:8,
		readid:document.getElementById("select_id_pa").selectedIndex,
		readstream:val1,
		writeid:document.getElementById("select_writeid_pa").selectedIndex,
		writestream:val2,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
		$(":button").attr('disabled',false);
	});
}

function writeOnOff_pa()
{
	$(":button").attr('disabled',true);
	var radioVal = 2;
	var radio1 = document.getElementById("radio_up_pa");
	var radio2 = document.getElementById("radio_down_pa");
	if(radio1.checked == true)
		radioVal = 1;
	else if(radio2.checked == true)
		radioVal = 0;
		
	var val = 2;
	if($("#button_onOff_pa").text() == "关闭模块")
		val = 0;
	else if($("#button_onOff_pa").text() == "打开模块")
		val = 1;
		
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:9,
		readid:document.getElementById("select_id_pa").selectedIndex,
		readstream:radioVal,
		onoff:val,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
			if($("#button_onOff_pa").text() == "关闭模块")
				$("#button_onOff_pa").text("打开模块");
			else if($("#button_onOff_pa").text() == "打开模块")
				$("#button_onOff_pa").text("关闭模块");
		}
		else alert("error");
		$(":button").attr('disabled',false);
	});
}

function writeDecay_pa()
{
	$(":button").attr('disabled',true);
	var radioVal = 2;
	var radio1 = document.getElementById("radio_up_pa");
	var radio2 = document.getElementById("radio_down_pa");
	if(radio1.checked == true)
		radioVal = 1;
	else if(radio2.checked == true)
		radioVal = 0;
		
	var val2 = 2;
	var radio3 = document.getElementById("radio_save_pa");
	var radio4 = document.getElementById("radio_noSave_pa");
	if(radio3.checked == true)
		val2 = 0;
	else if(radio4.checked == true)
		val2 = 1;
		
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:10,
		readid:document.getElementById("select_id_pa").selectedIndex,
		readstream:radioVal,
		save:val2,
		step:document.getElementById("select_step_pa").selectedIndex,
		decay:$("#textbox_decay_pa").val(),
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
		$(":button").attr('disabled',false);
	});
}

function writeALC_pa()
{
	$(":button").attr('disabled',true);
	var radioVal = 2;
	var radio1 = document.getElementById("radio_up_pa");
	var radio2 = document.getElementById("radio_down_pa");
	if(radio1.checked == true)
		radioVal = 1;
	else if(radio2.checked == true)
		radioVal = 0;
		
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:11,
		readid:document.getElementById("select_id_pa").selectedIndex,
		readstream:radioVal,
		alc:$("#textbox_alc_pa").val(),
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
		$(":button").attr('disabled',false);
	});
}

function goindex()
{
	var admin=$("#adminbutton",parent.document).text();
	if(admin =="" ||admin==null)
	{
		window.location.href="index.html";
	}
}

window.onload = function(){
    goindex();
}

function readVersion_pa()
{
	$(":button").attr('disabled',true);
	var radioVal = 2;
	var radio1 = document.getElementById("radio_up_pa");
	var radio2 = document.getElementById("radio_down_pa");
	if(radio1.checked == true)
		radioVal = 1;
	else if(radio2.checked == true)
		radioVal = 0;
		
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:12,
		readid:document.getElementById("select_id_pa").selectedIndex,
		readstream:radioVal,
	},function(data,status){
		if(status == "success"){
			try{
				var obj = JSON.parse(data);
				$("#span_version_pa").text(obj.version);
				LogDebug(LogMsgType.Normal,"软件版本："+obj.version);
			}
			catch(e){
				LogDebug(LogMsgType.Normal,data);
			}
		}
		else alert("error");
		$(":button").attr('disabled',false);
	});
}

function writeOffset_pa()
{
	$.post("/cgi-bin/pa.cgi",{
		cgiNumber:13,
		offset_forward:$("#textbox_offset_pa_forward").val(),
		offset_input:$("#textbox_offset_pa_input").val(),
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}
