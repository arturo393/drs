function setCtrl()
{
	$.post("/cgi-bin/test.cgi",{
		cgiNumber:1,
		reg0:$("#adc_test_on").val(),
		reg1:$("#dac_test_mode").val(),
		reg2:$("#gui_dcs").val(),
		reg3:$("#lb_mode").val(),
		reg4:$("#dac_test_mode5").val(),
		reg5:$("#ctl_register5").val(),
		reg6:$("#ctl_register6").val(),
		reg7:$("#ctl_register7").val(),
	},
	function(data,status){
		if(status == "success")
		{
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});	
}

function getCtrl()
{
	$.post("/cgi-bin/test.cgi",{
		cgiNumber:2,
	},
	function(data,status){
		if(status == "success")
		{
			var obj = JSON.parse(data);
			$("#adc_test_on").val(obj.adc_test_on);
			$("#dac_test_mode").val(obj.dac_test_mode);
			$("#gui_dcs").val(obj.gui_dcs);
			$("#lb_mode").val(obj.lb_mode);
			$("#dac_test_mode5").val(obj.dac_test_mode5);
			$("#ctl_register5").val(obj.clt_register5);
			$("#ctl_register6").val(obj.clt_register6);
			$("#ctl_register7").val(obj.clt_register7);
		}
		else alert("error");
	});	
}

function select_DataType_change()
{
	var obj = document.getElementById("select_getDataType");
	var datatype = obj.options[obj.selectedIndex].text;
	if(datatype == "FBDATA")
		$("#textbox_length").val("4048");
	else
		$("#textbox_length").val("65536");
}

function button_getIQData()
{
	var obj = document.getElementById("select_getDataType");
	$.post("/cgi-bin/test.cgi",{
		cgiNumber:4,
		type:document.getElementById("select_getDataType").selectedIndex,
		offset:$("#textbox_offsetAddr").val(),
		length:$("#textbox_length").val(),
	},
	function(data,status){
		LogDebug(LogMsgType.Normal,data);
		$("#downloadCapture")[0].click();
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
	getCtrl();
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
