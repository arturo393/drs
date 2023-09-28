//alc
function writeRx0Alc()
{
	var select = document.getElementById("select_rx0Switch");
	$.post("/cgi-bin/rx0.cgi",{
		cgiNumber:3,
		meanexp:$("#textbox_rx0MeanExp").val(),
		searchnum:$("#textbox_rx0SearchNum").val(),
		enable:select.selectedIndex,
		manualdatt:$("#textbox_rx0ManualDatt").val(),
		offsetdatt:$("#textbox_rx0OffsetDatt").val(),
		target:$("#textbox_rx0Target").val(),
		delaytime:$("#textbox_rx0DelayTime").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//使能开关
function writeRx0EnSwitch()
{
	$.post("/cgi-bin/rx0.cgi",{
		cgiNumber:4,
		gain:document.getElementById("checkbox_rx0GainCompSwitch").checked==true?1:0,
		temperature:document.getElementById("checkbox_rx0TempCompSwitch").checked==true?1:0,
		datt:document.getElementById("checkbox_rx0DattCompSwitch").checked==true?1:0,
		coe:document.getElementById("checkbox_rx0CoeCompSwitch").checked==true?1:0,
		rfpoint:document.getElementById("checkbox_rx0ChRfPointSwitch").checked==true?1:0,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//增益补偿
function writeRx0GainVal()
{
	var b = /^\d+(\.\d+)?$/;
	if(!b.test($("#textbox_rx0GainVal").val()))
	{
		LogDebug(LogMsgType.Error,"value should be:0.50~1.99");
		return ;
	}
	var gain = parseFloat($("#textbox_rx0GainVal").val());
	if(isNaN(gain) || gain<0 || gain>1.99)
	{
		LogDebug(LogMsgType.Error,"value should be:0.50~1.99");
		return ;
	}
	$.post("/cgi-bin/rx0.cgi",{
		cgiNumber:5,
		gaincompval:$("#textbox_rx0GainVal").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});

}

function writeRx0TempTable()
{
	$("#file_rx0TempTable").click();
}
//温度补偿
function rx0TempTable()
{
	var i = 40;//140;
	var tempurature = new Array();
	var selectedFile = document.getElementById("file_rx0TempTable").files[0];

	var reader = new FileReader();
	reader.onload = function(){
		var jsonVal = ParseINIString(this.result);
		for(x in jsonVal)
		{
			if(x == "rx0 temperature compensate table")
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
					url: '/cgi-bin/rx0.cgi',  
					contentType : "application/x-www-form-urlencoded" ,
					data : {"cgiNumber":14,"tempTable":JSON.stringify(tempurature)}, 
					success : function(data) {  
						LogDebug(LogMsgType.Normal,data);
						$("#file_rx0TempTable").val("");
					}  
				});
				break;
			}
		}
	};

	reader.readAsText(selectedFile);
}
//alc控制差值门限
function writeRx0AlcCtrlThreshold()
{
	if($("#textbox_rx0AlcThresholdVal").val()=="") 
	{
		LogDebug(LogMsgType.Error,"input the value please!");
		return ;
	}
	var b = /^[0-9]*$/g;
	if(false == b.test($("#textbox_rx0AlcThresholdVal").val()))
	{
		LogDebug(LogMsgType.Error,"value should be:0~63");
		return ;
	}
	var n = parseInt($("#textbox_rx0AlcThresholdVal").val(),10);
	if(isNaN(n) || n<0 || n>63)
	{
		LogDebug(LogMsgType.Error,"value should be:0~63");
		return ;
	}
	var alc = document.getElementById("select_rx0AlcThresholdEn");
	$.post("/cgi-bin/rx0.cgi",{
		cgiNumber:7,
		enable:alc.selectedIndex,
		val:$("#textbox_rx0AlcThresholdVal").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//基带补偿
function writeRx0BbComp()
{
	$.post("/cgi-bin/rx0.cgi",{
		cgiNumber:8,
		val:$("#textbox_rx0BbComp").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//底噪
function writeRx0Noise()
{
	manual1=document.getElementById("checkbox_rx0Manual1").checked==true?1:0,
	manual2=document.getElementById("checkbox_rx0Manual2").checked==true?1:0,
	manual3=document.getElementById("checkbox_rx0Manual3").checked==true?1:0,
	manual4=document.getElementById("checkbox_rx0Manual4").checked==true?1:0,
	manual5=document.getElementById("checkbox_rx0Manual5").checked==true?1:0,
	manual6=document.getElementById("checkbox_rx0Manual6").checked==true?1:0,
	manual7=document.getElementById("checkbox_rx0Manual7").checked==true?1:0,
	manual8=document.getElementById("checkbox_rx0Manual8").checked==true?1:0,
	manual9=document.getElementById("checkbox_rx0Manual9").checked==true?1:0,
	manual10=document.getElementById("checkbox_rx0Manual10").checked==true?1:0,
	manual11=document.getElementById("checkbox_rx0Manual11").checked==true?1:0,
	manual12=document.getElementById("checkbox_rx0Manual12").checked==true?1:0,
	manual13=document.getElementById("checkbox_rx0Manual13").checked==true?1:0,
	manual14=document.getElementById("checkbox_rx0Manual14").checked==true?1:0,
	manual15=document.getElementById("checkbox_rx0Manual15").checked==true?1:0,
	manual16=document.getElementById("checkbox_rx0Manual16").checked==true?1:0,
	manual17=document.getElementById("checkbox_rx0Manual17").checked==true?1:0,
	manual18=document.getElementById("checkbox_rx0Manual18").checked==true?1:0,
	manual19=document.getElementById("checkbox_rx0Manual19").checked==true?1:0,
	manual20=document.getElementById("checkbox_rx0Manual20").checked==true?1:0,
	manual21=document.getElementById("checkbox_rx0Manual21").checked==true?1:0,
	manual22=document.getElementById("checkbox_rx0Manual22").checked==true?1:0,
	manual23=document.getElementById("checkbox_rx0Manual23").checked==true?1:0,
	manual24=document.getElementById("checkbox_rx0Manual24").checked==true?1:0,
	manual25=document.getElementById("checkbox_rx0Manual25").checked==true?1:0,
	manual26=document.getElementById("checkbox_rx0Manual26").checked==true?1:0,
	manual27=document.getElementById("checkbox_rx0Manual27").checked==true?1:0,
	manual28=document.getElementById("checkbox_rx0Manual28").checked==true?1:0,
	manual29=document.getElementById("checkbox_rx0Manual29").checked==true?1:0,
	manual30=document.getElementById("checkbox_rx0Manual30").checked==true?1:0,
	manual31=document.getElementById("checkbox_rx0Manual31").checked==true?1:0,
	manual32=document.getElementById("checkbox_rx0Manual32").checked==true?1:0,
	manuala = manual1 | manual2<<1 | manual3<<2 | manual4<<3 | manual5<<4 | manual6<<5 | manual7<<6 | manual8<<7
	| manual9<<8 | manual10<<9 | manual11<<10 | manual12<<11 | manual13<<12 | manual14<<13 | manual15<<14 | manual16<<15;
	manualb = manual17 | manual18<<1 | manual19<<2 | manual20<<3 | manual21<<4 | manual22<<5 | manual23<<6 | manual24<<7
	| manual25<<8 | manual26<<9 | manual27<<10 | manual28<<11 | manual29<<12 | manual30<<13 | manual31<<14 | manual32<<15;
	var noise = document.getElementById("select_rx0LowNoise");
	$.post("/cgi-bin/rx0.cgi",{
		cgiNumber:9,
		meanexp:$("#textbox_rx0NoiseMeanExp").val(),
		searchnum:$("#textbox_rx0NoiseSearchNum").val(),
		lownoise:noise.selectedIndex,
		manuala:manuala,
		manualb:manualb,
		highlevel:$("#textbox_rx0HighLevel").val()*256,
		lowlevel:$("#textbox_rx0LowLevel").val()*256,
		lowpwcnt:$("#textbox_rx0LowPwCnt").val(),
		leveloffset:$("#textbox_rx0LevelOffset").val()*256,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}

function readRx0()
{
	var select = document.getElementById("select_rx0Switch");
	$.post("/cgi-bin/rx0.cgi",{
		cgiNumber:12,
	},function(data,status){
		if(status == "success")
		{
			var obj = JSON.parse(data);
			$("#textbox_rx0MeanExp").val(obj.rx0MeanExp);
			$("#textbox_rx0SearchNum").val(obj.rx0SearchNum);
			select.selectedIndex = obj.rx0Switch;
			$("#textbox_rx0ManualDatt").val(obj.rx0ManualDatt.toFixed(2));
			$("#textbox_rx0OffsetDatt").val(obj.rx0OffsetDatt.toFixed(2));
			$("#textbox_rx0Target").val(obj.rx0Target.toFixed(3));
			$("#textbox_rx0DelayTime").val(obj.rx0DelayTime);
			if(obj.rx0GainCompSwitch == 1)
				document.getElementById("checkbox_rx0GainCompSwitch").checked = true;
			else
				document.getElementById("checkbox_rx0GainCompSwitch").checked = false;
			if(obj.rx0TempCompSwitch == 1)
				document.getElementById("checkbox_rx0TempCompSwitch").checked = true;
			else
				document.getElementById("checkbox_rx0TempCompSwitch").checked = false;
			if(obj.rx0DattCompSwitch == 1)
				document.getElementById("checkbox_rx0DattCompSwitch").checked = true;
			else
				document.getElementById("checkbox_rx0DattCompSwitch").checked = false;
			if(obj.rx0CoeCompSwitch == 1)
				document.getElementById("checkbox_rx0CoeCompSwitch").checked = true;
			else
				document.getElementById("checkbox_rx0CoeCompSwitch").checked = false;
			if(obj.rx0ChRfPointSwitch == 1)
				document.getElementById("checkbox_rx0ChRfPointSwitch").checked = true;
			else
				document.getElementById("checkbox_rx0ChRfPointSwitch").checked = false;
		
			$("#textbox_rx0GainVal").val(obj.rx0GainVal.toFixed(2));
			document.getElementById("select_rx0Coe").selectedIndex = obj.rx0Coe;
			document.getElementById("select_rx0AlcThresholdEn").selectedIndex = obj.rx0AlcThresholdEn;
			$("#textbox_rx0AlcThresholdVal").val(obj.rx0AlcThresholdVal);
			$("#textbox_rx0MaxVal").val(obj.rx0MaxVal);
			$("#textbox_rx0BbComp").val(obj.rx0BbComp);
			$("#textbox_rx0NoiseMeanExp").val(obj.rx0NoiseMeanExp);
			$("#textbox_rx0NoiseSearchNum").val(obj.rx0NoiseSearchNum);
			document.getElementById("select_rx0LowNoise").selectedIndex = obj.rx0LowNoise;
			var i = 1;
			for(y in obj.rx0Manual)
			{
				if(obj.rx0Manual[y] == 1)
					document.getElementById("checkbox_rx0Manual"+i++).checked = true;
				else
					document.getElementById("checkbox_rx0Manual"+i++).checked = false;
			}
			$("#textbox_rx0HighLevel").val((obj.rx0HighLevel/256).toFixed(2));
			$("#textbox_rx0LowLevel").val((obj.rx0LowLevel/256).toFixed(2));
			$("#textbox_rx0LowPwCnt").val(obj.rx0LowPwCnt);
			$("#span_rx0TempCompVal").text(obj.rx0TempComp);
			$("#textbox_rx0LevelOffset").val((obj.rx0LevelOffset/256).toFixed(2));
			
			if(obj.tx0GainCompSwitch == 1)
				document.getElementById("checkbox_tx0GainCompSwitch").checked = true;
			else
				document.getElementById("checkbox_tx0GainCompSwitch").checked = false;
			if(obj.tx0TempCompSwitch == 1)
				document.getElementById("checkbox_tx0TempCompSwitch").checked = true;
			else
				document.getElementById("checkbox_tx0TempCompSwitch").checked = false;
			if(obj.tx0DattCompSwitch == 1)
				document.getElementById("checkbox_tx0DattCompSwitch").checked = true;
			else
				document.getElementById("checkbox_tx0DattCompSwitch").checked = false;
			if(obj.tx0CoeCompSwitch == 1)
				document.getElementById("checkbox_tx0CoeCompSwitch").checked = true;
			else
				document.getElementById("checkbox_tx0CoeCompSwitch").checked = false;
			$("#textbox_tx0GainVal").val(obj.tx0GainVal.toFixed(2));
			$("#span_tx0TempCompVal").text(obj.tx0TempComp);
		}
		else alert("error");
	});
}

function writeRx0Filter()
{
	$("#file_rx0Filter").click();
}

function rx0Filter()
{
	var filter = new Array();
	var i = 0;
	var selectedFile = document.getElementById("file_rx0Filter").files[0];

	var reader = new FileReader();
	reader.onload = function(){
		var jsonVal = ParseINIString(this.result);
		for(x in jsonVal)
		{
			if(x == "rx0 filter table")
			{
				var data = GetValueFromJsonByKey(jsonVal,x);
				for(y in data)
				{
					filter[i] = data[y];
					i++;
				}
				$.post("/cgi-bin/rx0.cgi",{
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
					$("#file_rx0Filter").val("");
				});
				break;
			}
		}
	};

	reader.readAsText(selectedFile);
}
//使能开关
function writeTx0ComeEn()
{
	$.post("/cgi-bin/rx0.cgi",{
		cgiNumber:16,
		gain:document.getElementById("checkbox_tx0GainCompSwitch").checked==true?1:0,
		temperature:document.getElementById("checkbox_tx0TempCompSwitch").checked==true?1:0,
		datt:document.getElementById("checkbox_tx0DattCompSwitch").checked==true?1:0,
		coe:document.getElementById("checkbox_tx0CoeCompSwitch").checked==true?1:0,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}
//增益补偿
function writeTx0GainVal()
{
	var b = /^\d+(\.\d+)?$/;
	if(!b.test($("#textbox_tx0GainVal").val()))
	{
		LogDebug(LogMsgType.Error,"value should be:0.50~1.99");
		return ;
	}
	var gain = parseFloat($("#textbox_tx0GainVal").val());
	if(isNaN(gain) || gain<0 || gain>1.99)
	{
		LogDebug(LogMsgType.Error,"value should be:0.50~1.99");
		return ;
	}
	$.post("/cgi-bin/rx0.cgi",{
		cgiNumber:17,
		gaincompval:gain,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}

function writeTx0TempTable()
{
	$("#file_tx0TempTable").click();
}
//温度补偿
function tx0TempTable()
{
	var i = 40;//140;
	var tempurature = new Array();
	var selectedFile = document.getElementById("file_tx0TempTable").files[0];

	var reader = new FileReader();
	reader.onload = function(){
		var jsonVal = ParseINIString(this.result);
		for(x in jsonVal)
		{
			if(x == "tx0 temperature compensate table")
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
					url: '/cgi-bin/rx0.cgi',  
					contentType : "application/x-www-form-urlencoded" ,
					data : {"cgiNumber":18,"tempTable":JSON.stringify(tempurature)}, 
					success : function(data) {  
						LogDebug(LogMsgType.Normal,data);
						$("#file_tx0TempTable").val("");
					}  
				});
				break;
			}
		}
	};

	reader.readAsText(selectedFile);
}

function writeTx0Filter()
{
	$("#file_tx0Filter").click();
}

function tx0Filter()
{
	var filter = new Array();
	var i = 0;
	var selectedFile = document.getElementById("file_tx0Filter").files[0];

	var reader = new FileReader();
	reader.onload = function(){
		var jsonVal = ParseINIString(this.result);
		for(x in jsonVal)
		{
			if(x == "tx0 filter table")
			{
				var data = GetValueFromJsonByKey(jsonVal,x);
				for(y in data)
				{
					filter[i] = data[y];
					i++;
				}
				$.post("/cgi-bin/rx0.cgi",{
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
					$("#file_tx0Filter").val("");
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
	readRx0();
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
