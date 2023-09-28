function initPeripheralHw()
{
	$("#file_peripheralHw").click();
}

function peripheralHw()
{
	$(":button").attr('disabled',true);
	$("a").css("pointer-events","none");
	var block = 10*1024; // 每次读取
	var file;// 当前文件对象
	var fileLoaded;// 当前已读取大小
	var fileSize;// 文件总大小
	var blob;

	file = document.getElementById("file_peripheralHw").files[0];
	fileLoaded = 0;
	fileSize = file.size;
	if(window.FileReader)//检测，ie10及以上支持
	{
		LogDebug(LogMsgType.Normal,"FileReader supported by your browser!");
		LogDebug(LogMsgType.Normal,"importing...waiting please");
		var reader = new FileReader();
		// 每个blob读取完毕时调用
		reader.onload = function(e) {
			var bb = new Blob([this.result]);
			var xhr = new XMLHttpRequest();
			xhr.open("POST", "/cgi-bin/uploadFileReader.cgi", false);//cgiTarget
			xhr.send(bb);
		   	fileLoaded += e.loaded;
			var percent = fileLoaded / fileSize;
			//LogUpdate(LogMsgType.Normal,"上传进度："+(percent*100).toFixed(2)+"%");
			if(percent < 1)  {
				// 继续读取下一块
				if(file.webkitSlice) {
					blob = file.webkitSlice(fileLoaded, fileLoaded + block + 1);
				} else if(file.mozSlice) {
					blob = file.mozSlice(fileLoaded, fileLoaded + block + 1);
				} else if(file.slice) {
					blob = file.slice(fileLoaded, fileLoaded + block + 1);
				} else {
					LogDebug(LogMsgType.Error,'unsuported section！');
					return false;
				}
				reader.readAsArrayBuffer(blob);
			} else {
				// 结束
				percent = 1;
				//再提交一个请求升级
				$.post("/cgi-bin/hwconfig.cgi",{
					cgiNumber:25,
				},
				function(data,status){
					if(status == "success")
						LogDebug(LogMsgType.Normal,data);
					else LogDebug(LogMsgType.Normal,"imported fauilure！");
					$("#file_peripheralHw").val("");
					$(":button").attr('disabled',false);
					$("a").css("pointer-events","auto");
				});
			}
		}
		// 开始读取
		if(file.webkitSlice) {
			blob = file.webkitSlice(fileLoaded, fileLoaded + block + 1);
		} else if(file.mozSlice) {
			blob = file.mozSlice(fileLoaded, fileLoaded + block + 1);
		} else if(file.slice) {
			blob = file.slice(fileLoaded, fileLoaded + block + 1);
		} else {
			LogDebug(LogMsgType.Error,'unsuported section！');
			return false;
		}
		reader.readAsArrayBuffer(blob);
	}
	else
	{
		LogDebug(LogMsgType.Normal,"FileReader not supported by your browser!");
	}
}

function initDac()
{
	$("#file_dac").click();
}

function dac()
{
	var i = 0,j = 0;
	var addr0 = new Array();
	var dac0 = new Array();
	var addr1 = new Array();
	var dac1 = new Array();
	var selectedFile = document.getElementById("file_dac").files[0];

	var reader = new FileReader();
	reader.onload = function(){
		var jsonVal = ParseINIString(this.result);
		for(x in jsonVal)
		{
			if(x == "dac0 config" || x == "dac1 config")
			{
				var data = GetValueFromJsonByKey(jsonVal,x);
				for(y in data)
				{
					if(x == "dac0 config")
					{
						addr0[i] = y;
						dac0[i] = data[y];
						i++;
					}
					else if(x == "dac1 config")
					{
						addr1[j] = y;
						dac1[j] = data[y];
						j++;
					}
				}
				if(i == 24 && j == 24)
				{
					$.ajax({  
						type : 'POST',  
						url: '/cgi-bin/hwconfig.cgi',  
						contentType : "application/x-www-form-urlencoded" ,
						data : {"cgiNumber":23,"addr0":JSON.stringify(addr0),"dac0":JSON.stringify(dac0),"addr1":JSON.stringify(addr1),"dac1":JSON.stringify(dac1)}, 
						success : function(data) {  
							LogDebug(LogMsgType.Normal,data);
							$("#file_dac").val("");
						}  
					});
					break;
				}
			}
		}
	};

	reader.readAsText(selectedFile);
}

function initHmc1197()
{
	$("#file_hmc1197").click();
}

function hmc1197()
{
	var i = 0,j = 0;
	var addr0 = new Array();
	var hmc0 = new Array();
	var addr1 = new Array();
	var hmc1 = new Array();
	var selectedFile = document.getElementById("file_hmc1197").files[0];

	var reader = new FileReader();
	reader.onload = function(){
		var jsonVal = ParseINIString(this.result);
		for(x in jsonVal)
		{
			if(x == "hmc1197a config" || x == "hmc1197b config")
			{
				var data = GetValueFromJsonByKey(jsonVal,x);
				for(y in data)
				{
					if(x == "hmc1197a config")
					{
						addr0[i] = y;
						hmc0[i] = data[y];
						i++;
					}
					else if(x == "hmc1197b config")
					{
						addr1[j] = y;
						hmc1[j] = data[y];
						j++;
					}
				}
				if(i == 18 && j == 18)
				{
					$.ajax({  
						type : 'POST',  
						url: '/cgi-bin/hwconfig.cgi',  
						contentType : "application/x-www-form-urlencoded" ,
						data : {"cgiNumber":24,"addr0":JSON.stringify(addr0),"hmc0":JSON.stringify(hmc0),"addr1":JSON.stringify(addr1),"hmc1":JSON.stringify(hmc1)}, 
						success : function(data) {  
							LogDebug(LogMsgType.Normal,data);
							$("#file_hmc1197").val("");
						}  
					});
					break;
				}
			}
		}
	};

	reader.readAsText(selectedFile);
}

function writeDac0()
{
	var radioVal = 2;
	var radio1 = document.getElementById("radio_dac0Normal");
	var radio2 = document.getElementById("radio_dac0Powerdown");
	if(radio1.checked == true)
		radioVal = 0;
	else if(radio2.checked == true)
		radioVal = 1;
	else
		radioVal = 2;

	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:1,
		dac0I:$("#textbox_dac0I").val(),
		dac0Q:$("#textbox_dac0Q").val(),
		radioDac0:radioVal,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function writeDac1()
{
	var radioVal = 2;
	var radio1 = document.getElementById("radio_dac1Normal");
	var radio2 = document.getElementById("radio_dac1Powerdown");
	if(radio1.checked == true)
		radioVal = 0;
	else if(radio2.checked == true)
		radioVal = 1;
	else
		radioVal = 2;

	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:2,
		dac1I:$("#textbox_dac1I").val(),
		dac1Q:$("#textbox_dac1Q").val(),
		radioDac1:radioVal,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function writeDatt()
{
	var b = /^\d+(\.\d+)?$/;
	if(!b.test($("#textbox_dattRx00").val()))
	{
		LogDebug(LogMsgType.Error,"value should be:0~31.5");
		return ;
	}
	if(!b.test($("#textbox_dattRx10").val()))
	{
		LogDebug(LogMsgType.Error,"value should be:0~31.5");
		return ;
	}
	if(!b.test($("#textbox_dattTx0").val()))
	{
		LogDebug(LogMsgType.Error,"value should be::0~31.5");
		return ;
	}
	if(!b.test($("#textbox_dattTx1").val()))
	{
		LogDebug(LogMsgType.Error,"value should be::0~31.5");
		return ;
	}
	var datt0 = parseFloat($("#textbox_dattRx00").val());
	var datt1 = parseFloat($("#textbox_dattRx10").val());
	var datt2 = parseFloat($("#textbox_dattTx0").val());
	var datt3 = parseFloat($("#textbox_dattTx1").val());
	if(isNaN(datt0) || isNaN(datt1) || isNaN(datt2) || isNaN(datt3) 
		|| datt0<0 || datt0>31.5 || datt1<0 || datt1>31.5 
		|| datt2<0 || datt2>31.5 || datt3<0 || datt3>31.5)
	{
		LogDebug(LogMsgType.Error,"value should be:0~31.5");
		return ;
	}
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:4,
		rx0_0:datt0,
		rx0_1:$("#textbox_dattRx01").val(),
		rx1_0:datt1,
		rx1_1:$("#textbox_dattRx11").val(),
		tx0:datt2,
		tx1:datt3,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function writeAd5662()
{
	var ad = document.getElementById("select_ad5662Manual");

	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:5,
		mode:ad.selectedIndex,
		parameter:$("#textbox_ad5662Val").val(),
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function afcReset()
{
	var afc;
	if($("#button_afcRst").text() == "复位")
	{
		afc = 1;
		$("#button_afcRst").text("解除");
	}
	else if($("#button_afcRst").text() == "解除")
	{
		afc = 0;
		$("#button_afcRst").text("复位");
	}
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:6,
		afcReset:afc,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function writeAfc()
{
	var mode = document.getElementById("select_afcMode");
	var auto = document.getElementById("select_afcAuto");
	var hand = document.getElementById("select_afcHand");
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:7,
		mode:mode.selectedIndex,
		autolightport:auto.selectedIndex,
		handlightport:hand.selectedIndex,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function readDac0()
{
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:15,
	},function(data,status){
		if(status == "success"){
			var obj = JSON.parse(data);
			for(x in obj.dac0)
				LogDebug(LogMsgType.Normal,"AD9122-0 register get:: reg:0x"+obj.addr0[x].toString(16)+", value:0x"+obj.dac0[x].toString(16));
		}
		else alert("error");
	});
}

function readDac1()
{
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:16,
	},function(data,status){
		if(status == "success"){
			var obj = JSON.parse(data);
			for(x in obj.dac1)
				LogDebug(LogMsgType.Normal,"AD9122-1 register get:: reg:0x"+obj.addr1[x].toString(16)+", value:0x"+obj.dac1[x].toString(16));
		}
		else alert("error");
	});
}

function readHmc0()
{
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:17,
	},function(data,status){
		if(status == "success"){
			var obj = JSON.parse(data);
			for(x in obj.hmc0)
				LogDebug(LogMsgType.Normal,"HMC1197-0 register get:: reg:0x"+obj.addr0[x].toString(16)+", value:0x"+obj.hmc0[x].toString(16));
		}
		else alert("error");
	});
}

function readHmc1()
{
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:18,
	},function(data,status){
		if(status == "success"){
			var obj = JSON.parse(data);
			for(x in obj.hmc1)
				LogDebug(LogMsgType.Normal,"HMC1197-1 register get:: reg:0x"+obj.addr1[x].toString(16)+", value:0x"+obj.hmc1[x].toString(16));
		}
		else alert("error");
	});
}

function readHwConfig()
{
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:22,
	},function(data,status){
		if(status == "success"){
			var obj = JSON.parse(data);
			$("#textbox_dattRx00").val(obj.dattRx00);
			$("#textbox_dattRx01").val(obj.dattRx01);
			$("#textbox_dattRx10").val(obj.dattRx10);
			$("#textbox_dattRx11").val(obj.dattRx11);
			$("#textbox_dattTx0").val(obj.dattTx0);
			$("#textbox_dattTx1").val(obj.dattTx1);
			document.getElementById("select_ad5662Manual").selectedIndex = obj.ad5662Manual;
			$("#textbox_ad5662Val").val(obj.ad5662Val);
			//LogDebug(LogMsgType.Normal,"afcReset:"+obj.afcReset);
			document.getElementById("select_afcMode").selectedIndex = obj.afcMode;
			document.getElementById("select_afcAuto").selectedIndex = obj.afcAuto;
			document.getElementById("select_afcHand").selectedIndex = obj.afcHand;
			$("#textbox_vcxoTrueValue").val(obj.vcxoTrueVal);
			$("#textbox_dac0I").val(obj.dac0[8] | obj.dac0[9] << 8);
			$("#textbox_dac0Q").val(obj.dac0[10] | obj.dac0[11] << 8);
			if(obj.dac0[2] == 0x10)
				document.getElementById("radio_dac0Normal").checked = true;
			else if(obj.dac0[2] == 0xf0)
				document.getElementById("radio_dac0Powerdown").checked = true;
			$("#textbox_dac1I").val(obj.dac1[8] | obj.dac1[9] << 8);
			$("#textbox_dac1Q").val(obj.dac1[10] | obj.dac1[11] << 8);
			if(obj.dac1[2] == 0x10)
				document.getElementById("radio_dac1Normal").checked = true;
			else if(obj.dac1[2] == 0xf0)
				document.getElementById("radio_dac1Powerdown").checked = true;
			if(obj.rf_switch == 0x0)
				document.getElementById("radio_RFOpen").checked = true;
			else if(obj.rf_switch == 0x1)
				document.getElementById("radio_RFClose").checked = true;
			$("#textbox_input_power_rx0").val(obj.rx0_power.toFixed(2));
			$("#textbox_input_power_rx1").val(obj.rx1_power.toFixed(2));
			$("#textbox_output_power_tx0").val(obj.tx0_power.toFixed(2));
			$("#textbox_output_power_tx1").val(obj.tx1_power.toFixed(2));
			$("#textbox_input_power_rx0_offset").val(obj.rx0_offset);
			$("#textbox_input_power_rx1_offset").val(obj.rx1_offset);
			$("#textbox_output_power_tx0_offset").val(obj.tx0_offset);
			$("#textbox_output_power_tx1_offset").val(obj.tx1_offset);
			$("#textBox_temp").val(obj.temperature.toFixed(1));
			if((obj.lockStatus & 0x01) == 0x01)
				$("#div_9524PLL2").css("background-color","green");
			else $("#div_9524PLL2").css("background-color","red");
			if((obj.lockStatus >> 1 & 0x01) == 0x01)
				$("#div_HMC1197A").css("background-color","green");
			else $("#div_HMC1197A").css("background-color","red");
			if((obj.lockStatus >> 2 & 0x01) == 0x01)
				$("#div_HMC1197B").css("background-color","green");
			else $("#div_HMC1197B").css("background-color","red");
			if((obj.lockStatus >>3 & 0x01) == 0x01)
				$("#div_AFC").css("background-color","green");
			else $("#div_AFC").css("background-color","red");
			$("#span_fpgaVersion").text(obj.fpgaVersion);
			$("#span_softVersion").text(obj.softVersion);
			$("#span_kernelVersion").text(obj.kernelVersion);
				$("#span_fbTx1Power").text(obj.fbTx1Power.toFixed(2)+"dBm");
				$("#span_fbRx1Power").text(obj.fbRx1Power.toFixed(2)+"dBm");
				$("#span_fbTx2Power").text(obj.fbTx2Power.toFixed(2)+"dBm");
				$("#span_fbRx2Power").text(obj.fbRx2Power.toFixed(2)+"dBm");
				$("#span_fbTx3Power").text(obj.fbTx3Power.toFixed(2)+"dBm");
				$("#span_fbRx3Power").text(obj.fbRx3Power.toFixed(2)+"dBm");
				$("#span_fbTx4Power").text(obj.fbTx4Power.toFixed(2)+"dBm");
				$("#span_fbRx4Power").text(obj.fbRx4Power.toFixed(2)+"dBm");
			$("#span_fbTemp1").text(obj.fbTemp1.toFixed(1)+"℃");
			$("#span_fbTemp2").text(obj.fbTemp2.toFixed(1)+"℃");
			$("#span_fbTemp3").text(obj.fbTemp3.toFixed(1)+"℃");
			$("#span_fbTemp4").text(obj.fbTemp4.toFixed(1)+"℃");
			$("#textBox_adcMaxOutputTx0").val(obj.dacMaxOutputTx0);
			$("#textBox_adcMaxOutputTx1").val(obj.dacMaxOutputTx1);
			$("#textBox_adcMaxInputRx0").val(obj.adcMaxInputRx0);
			$("#textBox_adcMaxInputRx1").val(obj.adcMaxInputRx1);
			if((obj.selfAlarm & 0x01) == 0x01)
				$("#div_selfAlarmRx0").css("background-color","red");
			else $("#div_selfAlarmRx0").css("background-color","GreenYellow");
			if((obj.selfAlarm >> 1 & 0x01) == 0x01)
				$("#div_selfAlarmRx1").css("background-color","red");
			else $("#div_selfAlarmRx1").css("background-color","GreenYellow");
		}
		else alert("error");
	});
}

function downloadConfigFile()
{
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:27,
	},
	function(data,status){
		if(status == "success")
		{
			var blob = new Blob([data],{type:"application/octet-stream;charset=utf-8"});
			saveAs(blob,"syspar.ini");
		}
		else alert("error");
	});
}

function ad9524()
{
	var ad9524 = new Array();
	var i = 0;
	var selectedFile = document.getElementById("file_ad9524").files[0];

	var reader = new FileReader();
	reader.onload = function(){
		var jsonVal = ParseINIString(this.result);
		for(x in jsonVal)
		{
			if(x == "ad9524 config")
			{
				var data = GetValueFromJsonByKey(jsonVal,x);
				for(y in data)
				{
					ad9524[i] = data[y];
					i++;
				}
				$.ajax({  
					type : 'POST',  
					url: '/cgi-bin/hwconfig.cgi',  
					contentType : "application/x-www-form-urlencoded" ,
					data : {"cgiNumber":28,"ad9524":JSON.stringify(ad9524)}, 
					success : function(data) {  
						LogDebug(LogMsgType.Normal,data);
						$("#file_ad9524").val("");
					}  
				});
				break;
			}
		}
	};

	reader.readAsText(selectedFile);
}

function initTemprature()
{
	$("#file_temprature").click();
}

function temprature()
{
	var i = 40,j = 40,k = 40,l = 40;
	var rx0 = new Array();
	var rx1 = new Array();
	var tx0 = new Array();
	var tx1 = new Array();
	var selectedFile = document.getElementById("file_temprature").files[0];

	var reader = new FileReader();
	reader.onload = function(){
		var jsonVal = ParseINIString(this.result);
		for(x in jsonVal)
		{
			if(x == "rx0 temperature compensate table" || x == "rx1 temperature compensate table" || x == "tx0 temperature compensate table" || x == "tx1 temperature compensate table")
			{
				var data = GetValueFromJsonByKey(jsonVal,x);
				for(y in data)
				{
					if(x == "rx0 temperature compensate table")
					{
						rx0[i] = data[y];
						i++;
						if(i == 166)
							i = 0;
					}
					else if(x == "rx1 temperature compensate table")
					{
						rx1[j] = data[y];
						j++;
						if(j == 166)
							j = 0;
					}
					else if(x == "tx0 temperature compensate table")
					{
						tx0[k] = data[y];
						k++;
						if(k == 166)
							k = 0;
					}
					else if(x == "tx1 temperature compensate table")
					{
						tx1[l] = data[y];
						l++;
						if(l == 166)
							l = 0;
					}
				}
				if(rx0.length == 166 && rx1.length == 166 && tx0.length == 166 && tx1.length == 166)
				{
					$.ajax({  
						type : 'POST',  
						url: '/cgi-bin/hwconfig.cgi',  
						contentType : "application/x-www-form-urlencoded" ,
						data : {"cgiNumber":30,"rx0":JSON.stringify(rx0),"rx1":JSON.stringify(rx1),"tx0":JSON.stringify(tx0),"tx1":JSON.stringify(tx1)},
						success : function(data) {  
							LogDebug(LogMsgType.Normal,data);
							$("#file_temprature").val("");
						}  
					});
					break;
				}
			}
		}
	};

	reader.readAsText(selectedFile);
}

function downloadTempFile()
{
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:31,
	},
	function(data,status){
		if(status == "success")
		{
			var blob = new Blob([data],{type:"application/octet-stream;charset=utf-8"});
			saveAs(blob,"tempcomp.ini");
		}
		else alert("error");
	});
}

function readAd9524()
{
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:32,
	},function(data,status){
		if(status == "success"){
			try{
				var obj = JSON.parse(data);
				i=0;
				for(x in obj.ad9524_addr)
					LogDebug(LogMsgType.Normal,"AD9524 register get:: reg_"+PreFixInterge((i++),2)+"_0x"+PreFixInterge(obj.ad9524_addr[x].toString(16),3)+", value:0x"+PreFixInterge(obj.ad9524_data[x].toString(16),2));
			}catch(e){
				LogDebug(LogMsgType.Normal,data);
			}
		}
		else alert("error");
	});
}

function writeRFSwitch()
{
	var radioVal = 2;
	var radio1 = document.getElementById("radio_RFOpen");
	var radio2 = document.getElementById("radio_RFClose");
	if(radio1.checked == true)
		radioVal = 0;
	else if(radio2.checked == true)
		radioVal = 1;
	else
		radioVal = 2;

	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:34,
		rf_switch:radioVal,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function writeInputPower()
{
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:35,
		rx0_offset:$("#textbox_input_power_rx0_offset").val(),
		rx1_offset:$("#textbox_input_power_rx1_offset").val(),
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function writeOutputPower()
{
	$.post("/cgi-bin/hwconfig.cgi",{
		cgiNumber:36,
		tx0_offset:$("#textbox_output_power_tx0_offset").val(),
		tx1_offset:$("#textbox_output_power_tx1_offset").val(),
	},function(data,status){
		if(status == "success"){
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

		$("#newware").attr("style","display: none");
		$("#dowconfig").attr("style","display: none");
		$("#DAChtml").attr("style","display: none");
		$("#outputpowerhtml").attr("style","display: none");
		$("#Datthtml").attr("style","display: none");
		$("#ad5662html").attr("style","display: none");
		$("#switchhtml").attr("style","display: none");	
		$("#admindisplay1").attr("style","display: none");		
		$("#admindisplay2").attr("style","display: none");		
	}else{
		$("#newware").removeAttr("style");
		$("#dowconfig").removeAttr("style");
		$("#DAChtml").removeAttr("style");
		$("#outputpowerhtml").removeAttr("style");
		$("#Datthtml").removeAttr("style");
		$("#ad5662html").removeAttr("style");
		$("#switchhtml").removeAttr("style");
		$("#admindisplay1").removeAttr("style");
		$("#admindisplay2").removeAttr("style");
	}
    goindex();
	readHwConfig();
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
