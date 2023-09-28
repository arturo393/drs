var m_drag_ns = 8;//值为8或16，表示一拖八或十六，对应需修改ST_ArmEbiFpgaProtocol.h中的宏MS_DRAG_N_SS
function localFbStatus()
{
	$.post("/cgi-bin/msfb.cgi",{
		cgiNumber:1,	
	},function(data,status){
		if(status == "success"){
			try{
				var obj = JSON.parse(data);
				if((obj.fbStatus & 0x01) == 0x01)
				{
					for(j=1;j<m_drag_ns+1;j++)
						$("#span_status_1_"+j).text("FB1 Disconnect");
				}
				else
				{
					for(j=1;j<m_drag_ns+1;j++)
						$("#span_status_1_"+j).text("FB1 Connect");
				}
				if((obj.fbStatus >> 1 & 0x01) == 0x01)
				{
					for(j=1;j<m_drag_ns+1;j++)
						$("#span_status_2_"+j).text("FB2 Disconnect");
				}
				else
				{
					for(j=1;j<m_drag_ns+1;j++)
						$("#span_status_2_"+j).text("FB2 Connect");
				}
				if((obj.fbStatus >> 2 & 0x01) == 0x01)
				{
					for(j=1;j<m_drag_ns+1;j++)
						$("#span_status_3_"+j).text("FB3 Disconnect");
				}
				else
				{
					for(j=1;j<m_drag_ns+1;j++)
						$("#span_status_3_"+j).text("FB3 Connect");
				}
				if((obj.fbStatus >> 3 & 0x01) == 0x01)
				{
					for(j=1;j<m_drag_ns+1;j++)
						$("#span_status_4_"+j).text("FB4 Disconnect");
				}
				else
				{
					for(j=1;j<m_drag_ns+1;j++)
						$("#span_status_4_"+j).text("FB4 Connect");
				}
				
				if((obj.fbStatus >> 4 & 0x01) == 0x01)
					for(j=1;j<m_drag_ns+1;j++)
						$("#td_status_1_"+j).css("background-color","Red");
				else
					for(j=1;j<m_drag_ns+1;j++)
						$("#td_status_1_"+j).css("background-color","YellowGreen");
				if((obj.fbStatus >> 5 & 0x01) == 0x01)
					for(j=1;j<m_drag_ns+1;j++)
						$("#td_status_2_"+j).css("background-color","Red");
				else
					for(j=1;j<m_drag_ns+1;j++)
						$("#td_status_2_"+j).css("background-color","YellowGreen");
				if((obj.fbStatus >> 6 & 0x01) == 0x01)
					for(j=1;j<m_drag_ns+1;j++)
						$("#td_status_3_"+j).css("background-color","Red");
				else
					for(j=1;j<m_drag_ns+1;j++)
						$("#td_status_3_"+j).css("background-color","YellowGreen");
				if((obj.fbStatus >> 7 & 0x01) == 0x01)
					for(j=1;j<m_drag_ns+1;j++)
						$("#td_status_4_"+j).css("background-color","Red");
				else
					for(j=1;j<m_drag_ns+1;j++)
						$("#td_status_4_"+j).css("background-color","YellowGreen");
			}catch(e){
				LogDebug(LogMsgType.Normal,data);
			}
		}
		else alert("error");
	});
}

function localReachTime()
{
	$.post("/cgi-bin/msfb.cgi",{
		cgiNumber:2,	
	},function(data,status){
		if(status == "success"){
			var obj = JSON.parse(data);
			var x = 0;
			for(i=1;i<5;i++)
				for(j=1;j<m_drag_ns+1;j++)
					$("#span_reach_"+i+"_"+j).text(obj.reachTime[x++]);
		}
		else alert("error");
	});
}

function localTop()
{
	$.post("/cgi-bin/msfb.cgi",{
		cgiNumber:3,	
	},function(data,status){
		if(status == "success"){
			try{
				var obj = JSON.parse(data);
				var x = 0;
				for(i=1;i<5;i++)
					for(j=1;j<m_drag_ns+1;j++)
						$("#span_mac_"+i+"_"+j).text(obj.mac[x++]);
			}catch(e){
				LogDebug(LogMsgType.Normal,data);
			}
		}
		else alert("error");
	});
}

function readCnfTime()
{
	$.post("/cgi-bin/msfb.cgi",{
		cgiNumber:4,	
	},function(data,status){
		if(status == "success"){
			var obj = JSON.parse(data);
			var x = 0;
			for(i=1;i<5;i++)
				for(j=1;j<m_drag_ns+1;j++)
					$("#span_delay_"+i+"_"+j).text(obj.delayTime[x++]);
		}
		else alert("error");
	});
}

function writeCnfTime()
{
	var delay = new Array();
	var x = 0;
	for(i=1;i<5;i++)
		for(j=1;j<m_drag_ns+1;j++)
			delay[x++] = $("#span_delay_"+i+"_"+j).text();

	$.ajax({  
		type : 'POST',  
		url: '/cgi-bin/msfb.cgi',  
		contentType : "application/x-www-form-urlencoded" ,
		data : {"cgiNumber":5,"delay":JSON.stringify(delay)}, 
		success : function(data) {  
			LogDebug(LogMsgType.Normal,data);
		}  
	});
}

function readSSID()
{
	$.post("/cgi-bin/msfb.cgi",{
		cgiNumber:6,	
	},function(data,status){
		if(status == "success"){
			var obj = JSON.parse(data);
			var x = 0;
			for(i=1;i<5;i++)
				for(j=1;j<m_drag_ns+1;j++)
					$("#span_id_"+i+"_"+j).text(obj.ssid[x++]);
		}
		else alert("error");
	});
}

function readAll()
{
	localFbStatus();
	readSSIP();
	localTop();
	readCnfTime();
	localReachTime();
	readSSID();
}

function readSSIP()
{
	$.post("/cgi-bin/msfb.cgi",{
		cgiNumber:12,	
	},function(data,status){
		if(status == "success"){
			var obj = JSON.parse(data);
			var x = 0;
			for(i=1;i<5;i++)
				for(j=1;j<m_drag_ns+1;j++)
					$("#span_ip_"+i+"_"+j).text(obj.ssip[x++]);
		}
		else alert("error");
	});
}

function initFb()
{
	$.post("/cgi-bin/msfb.cgi",{
		cgiNumber:7,	
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function writeLightPort()
{
	if($("#textbox_localMAC0").val()=="" || $("#textbox_localMAC1").val()=="" || 
		$("#textbox_localMAC2").val()=="" || $("#textbox_localMAC3").val()=="" )
	{
		LogDebug(LogMsgType.Error,"input the correct MAC please!");
		return ;
	}
	for(i = 0; i < 4; i++)
	{
		var b = /^[0-9a-zA-Z]*$/g;
		if(!b.test($("#textbox_localMAC"+i).val()))
		{
			LogDebug(LogMsgType.Error,"MAC value should be:00~FF");
			return ;
		}
	}
	var m1 = parseInt($("#textbox_localMAC0").val(),16);
	var m2 = parseInt($("#textbox_localMAC1").val(),16);
	var m3 = parseInt($("#textbox_localMAC2").val(),16);
	var m4 = parseInt($("#textbox_localMAC3").val(),16);
	if(isNaN(m1) || isNaN(m2) || isNaN(m3) || isNaN(m4))
	{
		LogDebug(LogMsgType.Error,"MAC value should be:00~FF");
		return ;
	}

	if($("#textbox_localID").val()=="") 
	{
		LogDebug(LogMsgType.Error,"input the correct ID please!");
		return ;
	}
	var b = /^[0-9]*$/g;
	if(false == b.test($("#textbox_localID").val()))
	{
		LogDebug(LogMsgType.Error,"ID value should be:0~65535");
		return ;
	}
	var n = parseInt($("#textbox_localID").val(),10);
	if(isNaN(n) || n<0 || n>65535)
	{
		LogDebug(LogMsgType.Error,"ID value should be:0~65535");
		return ;
	}

	var port0 = document.getElementById("select_lightPort0");
	var port1 = document.getElementById("select_lightPort1");
	var port2 = document.getElementById("select_lightPort2");
	var port3 = document.getElementById("select_lightPort3");
	var mode = document.getElementById("select_lightMode");
	$.post("/cgi-bin/msfb.cgi",{
		cgiNumber:8,
		lightport0:port0.selectedIndex,
		lightport1:port1.selectedIndex,
		lightport2:port2.selectedIndex,
		lightport3:port3.selectedIndex,
		mode:mode.selectedIndex,
		id:$("#textbox_localID").val(),
		mac1:m1,
		mac2:m2,
		mac3:m3,
		mac4:m4,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function readLightPort()
{
	var port0 = document.getElementById("select_lightPort0");
	var port1 = document.getElementById("select_lightPort1");
	var port2 = document.getElementById("select_lightPort2");
	var port3 = document.getElementById("select_lightPort3");
	var mode = document.getElementById("select_lightMode");
	$.post("/cgi-bin/msfb.cgi",{
		cgiNumber:9,
	},function(data,status){
		if(status == "success"){
			var obj = JSON.parse(data);
			port0.selectedIndex = obj.lightPort0;
			port1.selectedIndex = obj.lightPort1;
			port2.selectedIndex = obj.lightPort2;
			port3.selectedIndex = obj.lightPort3;
			mode.selectedIndex = obj.lightMode;
			$("#textbox_localID").val(obj.localID);
			$("#textbox_localMAC0").val(PreFixInterge(obj.localMAC0.toString(16).toUpperCase(),2));
			$("#textbox_localMAC1").val(PreFixInterge(obj.localMAC1.toString(16).toUpperCase(),2));
			$("#textbox_localMAC2").val(PreFixInterge(obj.localMAC2.toString(16).toUpperCase(),2));
			$("#textbox_localMAC3").val(PreFixInterge(obj.localMAC3.toString(16).toUpperCase(),2));
			$("#textbox_master_ip0").val(obj.ip4);
			$("#textbox_master_ip1").val(obj.ip3);
			$("#textbox_master_ip2").val(obj.ip2);
			$("#textbox_master_ip3").val(obj.ip1);
			document.getElementById("select_delay").selectedIndex = obj.onoff;
		}
		else alert("error");
	});
}

function writeMasterIP()
{
	for(i=0;i<4;i++)
	{
		if($("#textbox_master_ip"+i).val()=="") 
		{
			LogDebug(LogMsgType.Error,"input the correct ip addr please!");
			return ;
		}
		var b = /^[0-9]*$/g;
		if(false == b.test($("#textbox_master_ip"+i).val()))
		{
			LogDebug(LogMsgType.Error,"ip value should be:0~255");
			return ;
		}
		var n = parseInt($("#textbox_master_ip"+i).val(),10);
		if(isNaN(n) || n<0 || n>255)
		{
			LogDebug(LogMsgType.Error,"ip value should be:0~255");
			return ;
		}
	}
	$.post("/cgi-bin/msfb.cgi",{
		cgiNumber:10,
		ip1:$("#textbox_master_ip3").val(),
		ip2:$("#textbox_master_ip2").val(),
		ip3:$("#textbox_master_ip1").val(),
		ip4:$("#textbox_master_ip0").val(),
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function writeDelaySwitch()
{
	$.post("/cgi-bin/msfb.cgi",{
		cgiNumber:11,
		onoff:document.getElementById("select_delay").selectedIndex,
	},
	function(data,status){
		if(status == "success")
		{
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
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


window.onload=function(){
	var username=$("#adminbutton",parent.document).text();
	if(username=="Enter Admin"){
		
		$("#localFbStatushtml").attr("style","display: none");
		$("#readSSIPhtml").attr("style","display: none");
		$("#localTophtml").attr("style","display: none");
		$("#readCnfTimehtml").attr("style","display: none");
		$("#localReachTimehtml").attr("style","display: none");
		$("#readSSIDhtml").attr("style","display: none");	
		$("#confightml").attr("style","display: none");
	}else{
		$("#localFbStatushtml").removeAttr("style");
		$("#readSSIPhtml").removeAttr("style");
		$("#localTophtml").removeAttr("style");
		$("#readCnfTimehtml").removeAttr("style");
		$("#localReachTimehtml").removeAttr("style");
		$("#readSSIDhtml").removeAttr("style");
		$("#confightml").removeAttr("style");
	}
    goindex();
	readLightPort();
	$.post("/cgi-bin/test.cgi",{
	       cgiNumber:5,
	},
	function(data,status){
	       if(status == "success")
	       {
		       try{
		               var obj = JSON.parse(data);
		               $("#span_softwareVersion").text(obj.softVersion);
		       }catch(e){
		               LogDebug(LogMsgType.Normal,data);
		       }
	       }
	       else alert("error");
	});
}
