//alc
function writeRx1Alc()
{
	var select = document.getElementById("select_rx1Switch");
	$.post("/cgi-bin/rx1.cgi",{
		cgiNumber:3,
		meanexp:$("#textbox_rx1MeanExp").val(),
		searchnum:$("#textbox_rx1SearchNum").val(),
		enable:select.selectedIndex,
		manualdatt:$("#textbox_rx1ManualDatt").val(),
		offsetdatt:$("#textbox_rx1OffsetDatt").val(),
		target:$("#textbox_rx1Target").val(),
		delaytime:$("#textbox_rx1DelayTime").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//使能开关
function writeRx1EnSwitch()
{
	$.post("/cgi-bin/rx1.cgi",{
		cgiNumber:4,
		gain:document.getElementById("checkbox_rx1GainCompSwitch").checked==true?1:0,
		temperature:document.getElementById("checkbox_rx1TempCompSwitch").checked==true?1:0,
		datt:document.getElementById("checkbox_rx1DattCompSwitch").checked==true?1:0,
		coe:document.getElementById("checkbox_rx1CoeCompSwitch").checked==true?1:0,
		rfpoint:document.getElementById("checkbox_rx1ChRfPointSwitch").checked==true?1:0,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//增益补偿
function writeRx1GainVal()
{
	var b = /^\d+(\.\d+)?$/;
	if(!b.test($("#textbox_rx1GainVal").val()))
	{
		LogDebug(LogMsgType.Error,"请填入范围:0.50~1.99的值");
		return ;
	}
	var gain = parseFloat($("#textbox_rx1GainVal").val());
	if(isNaN(gain) || gain<0 || gain>1.99)
	{
		LogDebug(LogMsgType.Error,"请填入范围:0.50~1.99的值");
		return ;
	}
	$.post("/cgi-bin/rx1.cgi",{
		cgiNumber:5,
		gaincompval:$("#textbox_rx1GainVal").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});

}

function writeRx1TempTable()
{
	$("#file_rx1TempTable").click();
}
//温度补偿
function rx1TempTable()
{
	var i = 40;//140;
	var tempurature = new Array();
	var selectedFile = document.getElementById("file_rx1TempTable").files[0];

	var reader = new FileReader();
	reader.onload = function(){
		var jsonVal = ParseINIString(this.result);
		for(x in jsonVal)
		{
			if(x == "rx1 temperature compensate table")
			{
				var data = GetValueFromJsonByKey(jsonVal,x);
				for(y in data)
				{
					tempurature[i] = data[y];
					i++;
					if(i == 166)
						i = 0;
				}
				$.ajax({  
					type : 'POST',  
					url: '/cgi-bin/rx1.cgi',  
					contentType : "application/x-www-form-urlencoded" ,
					data : {"cgiNumber":14,"tempTable":JSON.stringify(tempurature)}, 
					success : function(data) {  
						LogDebug(LogMsgType.Normal,data);
						$("#file_rx1TempTable").val("");
					}  
				});
				break;
			}
		}
	};

	reader.readAsText(selectedFile);
}
//alc控制差值门限
function writeRx1AlcCtrlThreshold()
{
	if($("#textbox_rx1AlcThresholdVal").val()=="") 
	{
		LogDebug(LogMsgType.Error,"请填入值");
		return ;
	}
	var b = /^[0-9]*$/g;
	if(false == b.test($("#textbox_rx1AlcThresholdVal").val()))
	{
		LogDebug(LogMsgType.Error,"请填入正确的值:0~63");
		return ;
	}
	var n = parseInt($("#textbox_rx1AlcThresholdVal").val(),10);
	if(isNaN(n) || n<0 || n>63)
	{
		LogDebug(LogMsgType.Error,"请填入正确的值:0~63");
		return ;
	}
	var alc = document.getElementById("select_rx1AlcThresholdEn");
	$.post("/cgi-bin/rx1.cgi",{
		cgiNumber:7,
		enable:alc.selectedIndex,
		val:$("#textbox_rx1AlcThresholdVal").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//基带补偿
function writeRx1BbComp()
{
	$.post("/cgi-bin/rx1.cgi",{
		cgiNumber:8,
		val:$("#textbox_rx1BbComp").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//底噪
function writeRx1Noise()
{
	manual1=document.getElementById("checkbox_rx1Manual1").checked==true?1:0,
	manual2=document.getElementById("checkbox_rx1Manual2").checked==true?1:0,
	manual3=document.getElementById("checkbox_rx1Manual3").checked==true?1:0,
	manual4=document.getElementById("checkbox_rx1Manual4").checked==true?1:0,
	manual5=document.getElementById("checkbox_rx1Manual5").checked==true?1:0,
	manual6=document.getElementById("checkbox_rx1Manual6").checked==true?1:0,
	manual7=document.getElementById("checkbox_rx1Manual7").checked==true?1:0,
	manual8=document.getElementById("checkbox_rx1Manual8").checked==true?1:0,
	manual9=document.getElementById("checkbox_rx1Manual9").checked==true?1:0,
	manual10=document.getElementById("checkbox_rx1Manual10").checked==true?1:0,
	manual11=document.getElementById("checkbox_rx1Manual11").checked==true?1:0,
	manual12=document.getElementById("checkbox_rx1Manual12").checked==true?1:0,
	manual13=document.getElementById("checkbox_rx1Manual13").checked==true?1:0,
	manual14=document.getElementById("checkbox_rx1Manual14").checked==true?1:0,
	manual15=document.getElementById("checkbox_rx1Manual15").checked==true?1:0,
	manual16=document.getElementById("checkbox_rx1Manual16").checked==true?1:0,
	manual17=document.getElementById("checkbox_rx1Manual17").checked==true?1:0,
	manual18=document.getElementById("checkbox_rx1Manual18").checked==true?1:0,
	manual19=document.getElementById("checkbox_rx1Manual19").checked==true?1:0,
	manual20=document.getElementById("checkbox_rx1Manual20").checked==true?1:0,
	manual21=document.getElementById("checkbox_rx1Manual21").checked==true?1:0,
	manual22=document.getElementById("checkbox_rx1Manual22").checked==true?1:0,
	manual23=document.getElementById("checkbox_rx1Manual23").checked==true?1:0,
	manual24=document.getElementById("checkbox_rx1Manual24").checked==true?1:0,
	manual25=document.getElementById("checkbox_rx1Manual25").checked==true?1:0,
	manual26=document.getElementById("checkbox_rx1Manual26").checked==true?1:0,
	manual27=document.getElementById("checkbox_rx1Manual27").checked==true?1:0,
	manual28=document.getElementById("checkbox_rx1Manual28").checked==true?1:0,
	manual29=document.getElementById("checkbox_rx1Manual29").checked==true?1:0,
	manual30=document.getElementById("checkbox_rx1Manual30").checked==true?1:0,
	manual31=document.getElementById("checkbox_rx1Manual31").checked==true?1:0,
	manual32=document.getElementById("checkbox_rx1Manual32").checked==true?1:0,
	manuala = manual1 | manual2<<1 | manual3<<2 | manual4<<3 | manual5<<4 | manual6<<5 | manual7<<6 | manual8<<7
	| manual9<<8 | manual10<<9 | manual11<<10 | manual12<<11 | manual13<<12 | manual14<<13 | manual15<<14 | manual16<<15;
	manualb = manual17 | manual18<<1 | manual19<<2 | manual20<<3 | manual21<<4 | manual22<<5 | manual23<<6 | manual24<<7
	| manual25<<8 | manual26<<9 | manual27<<10 | manual28<<11 | manual29<<12 | manual30<<13 | manual31<<14 | manual32<<15;
	var noise = document.getElementById("select_rx1LowNoise");
	$.post("/cgi-bin/rx1.cgi",{
		cgiNumber:9,
		meanexp:$("#textbox_rx1NoiseMeanExp").val(),
		searchnum:$("#textbox_rx1NoiseSearchNum").val(),
		lownoise:noise.selectedIndex,
		manuala:manuala,
		manualb:manualb,
		highlevel:$("#textbox_rx1HighLevel").val()*256,
		lowlevel:$("#textbox_rx1LowLevel").val()*256,
		lowpwcnt:$("#textbox_rx1LowPwCnt").val(),
		leveloffset:$("#textbox_rx1LevelOffset").val()*256,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}

function readRx1()
{
	var select = document.getElementById("select_rx1Switch");
	$.post("/cgi-bin/rx1.cgi",{
		cgiNumber:12,
	},function(data,status){
		if(status == "success")
		{
			var obj = JSON.parse(data);
			$("#textbox_rx1MeanExp").val(obj.rx1MeanExp);
			$("#textbox_rx1SearchNum").val(obj.rx1SearchNum);
			select.selectedIndex = obj.rx1Switch;
			$("#textbox_rx1ManualDatt").val(obj.rx1ManualDatt.toFixed(2));
			$("#textbox_rx1OffsetDatt").val(obj.rx1OffsetDatt.toFixed(2));
			$("#textbox_rx1Target").val(obj.rx1Target.toFixed(3));
			$("#textbox_rx1DelayTime").val(obj.rx1DelayTime);
			if(obj.rx1GainCompSwitch == 1)
				document.getElementById("checkbox_rx1GainCompSwitch").checked = true;
			else
				document.getElementById("checkbox_rx1GainCompSwitch").checked = false;
			if(obj.rx1TempCompSwitch == 1)
				document.getElementById("checkbox_rx1TempCompSwitch").checked = true;
			else
				document.getElementById("checkbox_rx1TempCompSwitch").checked = false;
			if(obj.rx1DattCompSwitch == 1)
				document.getElementById("checkbox_rx1DattCompSwitch").checked = true;
			else
				document.getElementById("checkbox_rx1DattCompSwitch").checked = false;
			if(obj.rx1CoeCompSwitch == 1)
				document.getElementById("checkbox_rx1CoeCompSwitch").checked = true;
			else
				document.getElementById("checkbox_rx1CoeCompSwitch").checked = false;
			if(obj.rx1ChRfPointSwitch == 1)
				document.getElementById("checkbox_rx1ChRfPointSwitch").checked = true;
			else
				document.getElementById("checkbox_rx1ChRfPointSwitch").checked = false;
		
			$("#textbox_rx1GainVal").val(obj.rx1GainVal.toFixed(2));
			document.getElementById("select_rx1Coe").selectedIndex = obj.rx1Coe;
			document.getElementById("select_rx1AlcThresholdEn").selectedIndex = obj.rx1AlcThresholdEn;
			$("#textbox_rx1AlcThresholdVal").val(obj.rx1AlcThresholdVal);
			$("#textbox_rx1MaxVal").val(obj.rx1MaxVal);
			$("#textbox_rx1BbComp").val(obj.rx1BbComp);
			$("#textbox_rx1NoiseMeanExp").val(obj.rx1NoiseMeanExp);
			$("#textbox_rx1NoiseSearchNum").val(obj.rx1NoiseSearchNum);
			document.getElementById("select_rx1LowNoise").selectedIndex = obj.rx1LowNoise;
			var i = 1;
			for(y in obj.rx1Manual)
			{
				if(obj.rx1Manual[y] == 1)
					document.getElementById("checkbox_rx1Manual"+i++).checked = true;
				else
					document.getElementById("checkbox_rx1Manual"+i++).checked = false;
			}
			$("#textbox_rx1HighLevel").val((obj.rx1HighLevel/256).toFixed(2));
			$("#textbox_rx1LowLevel").val((obj.rx1LowLevel/256).toFixed(2));
			$("#textbox_rx1LowPwCnt").val(obj.rx1LowPwCnt);
			$("#span_rx1TempCompVal").text(obj.rx1TempComp);
			$("#textbox_rx1LevelOffset").val((obj.rx1LevelOffset/256).toFixed(2));
			
			if(obj.tx1GainCompSwitch == 1)
				document.getElementById("checkbox_tx1GainCompSwitch").checked = true;
			else
				document.getElementById("checkbox_tx1GainCompSwitch").checked = false;
			if(obj.tx1TempCompSwitch == 1)
				document.getElementById("checkbox_tx1TempCompSwitch").checked = true;
			else
				document.getElementById("checkbox_tx1TempCompSwitch").checked = false;
			if(obj.tx1DattCompSwitch == 1)
				document.getElementById("checkbox_tx1DattCompSwitch").checked = true;
			else
				document.getElementById("checkbox_tx1DattCompSwitch").checked = false;
			if(obj.tx1CoeCompSwitch == 1)
				document.getElementById("checkbox_tx1CoeCompSwitch").checked = true;
			else
				document.getElementById("checkbox_tx1CoeCompSwitch").checked = false;
			$("#textbox_tx1GainVal").val(obj.tx1GainVal.toFixed(2));
			$("#span_tx1TempCompVal").text(obj.tx1TempComp);
		}
		else alert("error");
	});
}

function writeRx1Filter()
{
	$("#file_rx1Filter").click();
}

function rx1Filter()
{
	var filter = new Array();
	var i = 0;
	var selectedFile = document.getElementById("file_rx1Filter").files[0];

	var reader = new FileReader();
	reader.onload = function(){
		var jsonVal = ParseINIString(this.result);
		for(x in jsonVal)
		{
			if(x == "rx1 filter table")
			{
				var data = GetValueFromJsonByKey(jsonVal,x);
				for(y in data)
				{
					filter[i] = data[y];
					i++;
				}
				$.post("/cgi-bin/rx1.cgi",{
					cgiNumber:15,
					para1:filter[0],para2:filter[1],para3:filter[2],para4:filter[3],
					para5:filter[4],para6:filter[5],para7:filter[6],para8:filter[7],
					para9:filter[8],para10:filter[9],para11:filter[10],para12:filter[11],
					para13:filter[12],para14:filter[13],
					para15:filter[14],para16:filter[15],para17:filter[16],para18:filter[17],
					para19:filter[18],para20:filter[19],para21:filter[20],para22:filter[21],
					para23:filter[22],para24:filter[23],para25:filter[24],para26:filter[25],
					para27:filter[26],para28:filter[27],para29:filter[28],para30:filter[29],
					para31:filter[30],para32:filter[31],
				},function(data,status){
					if(status == "success")
					{		
						LogDebug(LogMsgType.Normal,data);
					}
					else alert("error");
					$("#file_rx1Filter").val("");
				});
				break;
			}
		}
	};

	reader.readAsText(selectedFile);
}
//使能开关
function writeTx1ComeEn()
{
	$.post("/cgi-bin/rx1.cgi",{
		cgiNumber:16,
		gain:document.getElementById("checkbox_tx1GainCompSwitch").checked==true?1:0,
		temperature:document.getElementById("checkbox_tx1TempCompSwitch").checked==true?1:0,
		datt:document.getElementById("checkbox_tx1DattCompSwitch").checked==true?1:0,
		coe:document.getElementById("checkbox_tx1CoeCompSwitch").checked==true?1:0,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//增益补偿
function writeTx1GainVal()
{
	var b = /^\d+(\.\d+)?$/;
	if(!b.test($("#textbox_tx1GainVal").val()))
	{
		LogDebug(LogMsgType.Error,"请填入范围:0.50~1.99的值");
		return ;
	}
	var gain = parseFloat($("#textbox_tx1GainVal").val());
	if(isNaN(gain) || gain<0 || gain>1.99)
	{
		LogDebug(LogMsgType.Error,"请填入范围:0.50~1.99的值");
		return ;
	}
	$.post("/cgi-bin/rx1.cgi",{
		cgiNumber:17,
		gaincompval:gain,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}

function writeTx1TempTable()
{
	$("#file_tx1TempTable").click();
}
//温度补偿
function tx1TempTable()
{
	var i = 40;//140;
	var tempurature = new Array();
	var selectedFile = document.getElementById("file_tx1TempTable").files[0];

	var reader = new FileReader();
	reader.onload = function(){
		var jsonVal = ParseINIString(this.result);
		for(x in jsonVal)
		{
			if(x == "tx1 temperature compensate table")
			{
				var data = GetValueFromJsonByKey(jsonVal,x);
				for(y in data)
				{
					tempurature[i] = data[y];
					i++;
					if(i == 166)
						i = 0;
				}
				$.ajax({  
					type : 'POST',  
					url: '/cgi-bin/rx1.cgi',  
					contentType : "application/x-www-form-urlencoded" ,
					data : {"cgiNumber":18,"tempTable":JSON.stringify(tempurature)}, 
					success : function(data) {  
						LogDebug(LogMsgType.Normal,data);
						$("#file_tx1TempTable").val("");
					}  
				});
				break;
			}
		}
	};

	reader.readAsText(selectedFile);
}

function writeTx1Filter()
{
	$("#file_tx1Filter").click();
}

function tx1Filter()
{
	var filter = new Array();
	var i = 0;
	var selectedFile = document.getElementById("file_tx1Filter").files[0];

	var reader = new FileReader();
	reader.onload = function(){
		var jsonVal = ParseINIString(this.result);
		for(x in jsonVal)
		{
			if(x == "tx1 filter table")
			{
				var data = GetValueFromJsonByKey(jsonVal,x);
				for(y in data)
				{
					filter[i] = data[y];
					i++;
				}
				$.post("/cgi-bin/rx1.cgi",{
					cgiNumber:19,
					para1:filter[0],para2:filter[1],para3:filter[2],para4:filter[3],
					para5:filter[4],para6:filter[5],para7:filter[6],para8:filter[7],
					para9:filter[8],para10:filter[9],para11:filter[10],para12:filter[11],
					para13:filter[12],para14:filter[13],
					para15:filter[14],para16:filter[15],para17:filter[16],para18:filter[17],
					para19:filter[18],para20:filter[19],para21:filter[20],para22:filter[21],
					para23:filter[22],para24:filter[23],para25:filter[24],para26:filter[25],
					para27:filter[26],para28:filter[27],para29:filter[28],para30:filter[29],
					para31:filter[30],para32:filter[31],
				},function(data,status){
					if(status == "success")
						LogDebug(LogMsgType.Normal,data);
					else alert("error");
					$("#file_tx1Filter").val("");
				});
				break;
			}
		}
	};

	reader.readAsText(selectedFile);
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
    goindex();
	readRx1();
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
