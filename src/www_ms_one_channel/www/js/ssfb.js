function readSsFb()
{
	$.post("/cgi-bin/ssfb.cgi",{
		cgiNumber:1,
	},function(data,status){
		if(status == "success"){
			var obj = JSON.parse(data);
			if((obj.fbStatus & 0x01) == 0x01)
			{
				$("#span_fb1").css("color","Red");
				$("#span_fb1").text("FB1 Disconnect");
			}
			else
			{
				$("#span_fb1").css("color","YellowGreen");
				$("#span_fb1").text("FB1 Connect");
			}
			if((obj.fbStatus >> 1 & 0x01) == 0x01)
			{
				$("#span_fb2").css("color","Red");
				$("#span_fb2").text("FB2 Disconnect");
			}
			else
			{
				$("#span_fb2").css("color","YellowGreen");
				$("#span_fb2").text("FB2 Connect");
			}
			if((obj.fbStatus >> 2 & 0x01) == 0x01)
			{
				$("#span_fb3").css("color","Red");
				$("#span_fb3").text("FB3 Disconnect");
			}
			else
			{
				$("#span_fb3").css("color","YellowGreen");
				$("#span_fb3").text("FB3 Connect");
			}
			if((obj.fbStatus >> 3 & 0x01) == 0x01)
			{
				$("#span_fb4").css("color","Red");
				$("#span_fb4").text("FB4 Disconnect");
			}
			else
			{
				$("#span_fb4").css("color","YellowGreen");
				$("#span_fb4").text("FB4 Connect");
			}
			if((obj.fbStatus >> 4 & 0x01) == 0x01)
				$("#div_fb1").css("background-color","Red");
			else
				$("#div_fb1").css("background-color","GreenYellow");
			if((obj.fbStatus >> 5 & 0x01) == 0x01)
				$("#div_fb2").css("background-color","Red");
			else
				$("#div_fb2").css("background-color","GreenYellow");
			if((obj.fbStatus >> 6 & 0x01) == 0x01)
				$("#div_fb3").css("background-color","Red");
			else
				$("#div_fb3").css("background-color","GreenYellow");
			if((obj.fbStatus >> 7 & 0x01) == 0x01)
				$("#div_fb4").css("background-color","Red");
			else
				$("#div_fb4").css("background-color","GreenYellow");
			var netmode = document.getElementById("select_ssNetMode");
			netmode.selectedIndex = obj.ssNetMode;
			$("#textbox_localMaster").val(obj.lmodule);
			$("#textbox_remoteMAC0").val(PreFixInterge(obj.remoteMAC0.toString(16).toUpperCase(),2));
			$("#textbox_remoteMAC1").val(PreFixInterge(obj.remoteMAC1.toString(16).toUpperCase(),2));
			$("#textbox_remoteMAC2").val(PreFixInterge(obj.remoteMAC2.toString(16).toUpperCase(),2));
			$("#textbox_remoteMAC3").val(PreFixInterge(obj.remoteMAC3.toString(16).toUpperCase(),2));
			var delaymode0 = document.getElementById("select_ch0DelayMode");
			delaymode0.selectedIndex = obj.ch0DelayMode;
			var delaymode1 = document.getElementById("select_ch1DelayMode");
			delaymode1.selectedIndex = obj.ch1DelayMode;
			$("#textbox_ch0Delay").val(obj.ch0Delay.toFixed(3));
			$("#textbox_ch1Delay").val(obj.ch1Delay.toFixed(3));
			$("#textbox_ch0RecNetMode").val(obj.ch0RecNetMode);
			$("#textbox_ch1RecNetMode").val(obj.ch1RecNetMode);
			$("#textbox_ch0FbGain").val(obj.ch0FbGain.toFixed(2));
			$("#textbox_ch1FbGain").val(obj.ch1FbGain.toFixed(2));
			var fb1 = document.getElementById("select_fb1");
			fb1.selectedIndex = obj.fb1;
			var fb2 = document.getElementById("select_fb2");
			fb2.selectedIndex = obj.fb2;
			var fb3 = document.getElementById("select_fb3");
			fb3.selectedIndex = obj.fb3;
			var fb4 = document.getElementById("select_fb4");
			fb4.selectedIndex = obj.fb4;
			$("#textbox_ssId").val(obj.ssId);
			/*
			LogDebug(LogMsgType.Normal,"ip1 : "+obj.ip1);
			LogDebug(LogMsgType.Normal,"ip2 : "+obj.ip2);
			LogDebug(LogMsgType.Normal,"ip3 : "+obj.ip3);
			LogDebug(LogMsgType.Normal,"ip4 : "+obj.ip4);
			LogDebug(LogMsgType.Normal,"index1 : "+obj.index1);
			LogDebug(LogMsgType.Normal,"index2 : "+obj.index2);
			LogDebug(LogMsgType.Normal,"index3 : "+obj.index3);
			LogDebug(LogMsgType.Normal,"index4 : "+obj.index4);
			*/
		}
		else alert("error");
	});
}
//网络模式
function writeNetMode()
{
	var netmode = document.getElementById("select_ssNetMode");

	$.post("/cgi-bin/ssfb.cgi",{
		cgiNumber:2,
		mode:netmode.selectedIndex,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//mac
function writeMAC()
{
	if($("#textbox_remoteMAC0").val()=="" || $("#textbox_remoteMAC1").val()=="" || 
		$("#textbox_remoteMAC2").val()=="" || $("#textbox_remoteMAC3").val()=="" )
	{
		LogDebug(LogMsgType.Error,"input the correct MAC address please!");
		return ;
	}
	for(i = 0; i < 4; i++)
	{
		var b = /^[0-9a-zA-Z]*$/g;
		if(!b.test($("#textbox_remoteMAC"+i).val()))
		{
			LogDebug(LogMsgType.Error,"MAC value should be:00~FF");
			return ;
		}
	}
	var m1 = parseInt($("#textbox_remoteMAC0").val(),16);
	var m2 = parseInt($("#textbox_remoteMAC1").val(),16);
	var m3 = parseInt($("#textbox_remoteMAC2").val(),16);
	var m4 = parseInt($("#textbox_remoteMAC3").val(),16);
	if(isNaN(m1) || isNaN(m2) || isNaN(m3) || isNaN(m4))
	{
		LogDebug(LogMsgType.Error,"MAC value should be:00~FF");
		return ;
	}

	$.post("/cgi-bin/ssfb.cgi",{
		cgiNumber:3,
		mac1:m1,
		mac2:m2,
		mac3:m3,
		mac4:m4,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//延时
function writeRemoteDelay()
{
	var delaymode0 = document.getElementById("select_ch0DelayMode");
	var delaymode1 = document.getElementById("select_ch1DelayMode");

	$.post("/cgi-bin/ssfb.cgi",{
		cgiNumber:4,
		ch0delaycnfmode:delaymode0.selectedIndex,
		ch1delaycnfmode:delaymode1.selectedIndex,
		ch0delay:$("#textbox_ch0Delay").val(),
		ch1delay:$("#textbox_ch1Delay").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//增益
function writeChFbGain()
{
	for(i = 0; i < 2; i++)
	{
		var b = /^\d+(\.\d+)?$/;
		if(!b.test($("#textbox_ch"+i+"FbGain").val()))
		{
			LogDebug(LogMsgType.Error,"value should be:0.50~1.99");
			return ;
		}
	}
	var c0 = parseFloat($("#textbox_ch0FbGain").val());
	var c1 = parseFloat($("#textbox_ch1FbGain").val());
	if(isNaN(c0) || isNaN(c1) || c0<0.5 || c0>1.99 || c1<0.5 || c1>1.99)
	{
		LogDebug(LogMsgType.Error,"value should be:0.50~1.99");
		return ;
	}
	$.post("/cgi-bin/ssfb.cgi",{
		cgiNumber:5,
		ch0:c0,
		ch1:c1,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//光口开关
function writeFb()
{
	var fb1 = document.getElementById("select_fb1");
	var fb2 = document.getElementById("select_fb2");
	var fb3 = document.getElementById("select_fb3");
	var fb4 = document.getElementById("select_fb4");
	$.post("/cgi-bin/ssfb.cgi",{
		cgiNumber:6,
		lightport0:fb1.selectedIndex,
		lightport1:fb2.selectedIndex,
		lightport2:fb3.selectedIndex,
		lightport3:fb4.selectedIndex,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//id
function writeSsId()
{
	if($("#textbox_ssId").val()=="") 
	{
		LogDebug(LogMsgType.Error,"input the correct ID please!");
		return ;
	}
	var b = /^[0-9]*$/g;
	if(false == b.test($("#textbox_ssId").val()))
	{
		LogDebug(LogMsgType.Error,"ID value should be:0~65535");
		return ;
	}
	var n = parseInt($("#textbox_ssId").val(),10);
	if(isNaN(n) || n<0 || n>65535)
	{
		LogDebug(LogMsgType.Error,"ID value should be:0~65535");
		return ;
	}
	$.post("/cgi-bin/ssfb.cgi",{
		cgiNumber:7,
		id:$("#textbox_ssId").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//初始化
function initRemoteFb()
{
	$.post("/cgi-bin/ssfb.cgi",{
		cgiNumber:8,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
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
		
		$("#yanshihtml").attr("style","display: none");
		$("#guangxinhaohtml").attr("style","display: none");
	
		
	}else{
		$("#yanshihtml").removeAttr("style");
		$("#guangxinhaohtml").removeAttr("style");

	}
    goindex();
	readSsFb();	
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
