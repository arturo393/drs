//频点配置
function writeRx0Rfpoint()
{
	manual1=document.getElementById("checkbox_rx0Manual1").checked==true?0:1,
	manual2=document.getElementById("checkbox_rx0Manual2").checked==true?0:1,
	manual3=document.getElementById("checkbox_rx0Manual3").checked==true?0:1,
	manual4=document.getElementById("checkbox_rx0Manual4").checked==true?0:1,
	manual5=document.getElementById("checkbox_rx0Manual5").checked==true?0:1,
	manual6=document.getElementById("checkbox_rx0Manual6").checked==true?0:1,
	manual7=document.getElementById("checkbox_rx0Manual7").checked==true?0:1,
	manual8=document.getElementById("checkbox_rx0Manual8").checked==true?0:1,
	manual9=document.getElementById("checkbox_rx0Manual9").checked==true?0:1,
	manual10=document.getElementById("checkbox_rx0Manual10").checked==true?0:1,
	manual11=document.getElementById("checkbox_rx0Manual11").checked==true?0:1,
	manual12=document.getElementById("checkbox_rx0Manual12").checked==true?0:1,
	manual13=document.getElementById("checkbox_rx0Manual13").checked==true?0:1,
	manual14=document.getElementById("checkbox_rx0Manual14").checked==true?0:1,
	manual15=document.getElementById("checkbox_rx0Manual15").checked==true?0:1,
	manual16=document.getElementById("checkbox_rx0Manual16").checked==true?0:1,
	manual17=document.getElementById("checkbox_rx0Manual17").checked==true?0:1,
	manual18=document.getElementById("checkbox_rx0Manual18").checked==true?0:1,
	manual19=document.getElementById("checkbox_rx0Manual19").checked==true?0:1,
	manual20=document.getElementById("checkbox_rx0Manual20").checked==true?0:1,
	manual21=document.getElementById("checkbox_rx0Manual21").checked==true?0:1,
	manual22=document.getElementById("checkbox_rx0Manual22").checked==true?0:1,
	manual23=document.getElementById("checkbox_rx0Manual23").checked==true?0:1,
	manual24=document.getElementById("checkbox_rx0Manual24").checked==true?0:1,
	manual25=document.getElementById("checkbox_rx0Manual25").checked==true?0:1,
	manual26=document.getElementById("checkbox_rx0Manual26").checked==true?0:1,
	manual27=document.getElementById("checkbox_rx0Manual27").checked==true?0:1,
	manual28=document.getElementById("checkbox_rx0Manual28").checked==true?0:1,
	manual29=document.getElementById("checkbox_rx0Manual29").checked==true?0:1,
	manual30=document.getElementById("checkbox_rx0Manual30").checked==true?0:1,
	manual31=document.getElementById("checkbox_rx0Manual31").checked==true?0:1,
	manual32=document.getElementById("checkbox_rx0Manual32").checked==true?0:1,
	chx_off_on0 = manual1 | manual2<<1 | manual3<<2 | manual4<<3 | manual5<<4 | manual6<<5 | manual7<<6 | manual8<<7
	| manual9<<8 | manual10<<9 | manual11<<10 | manual12<<11 | manual13<<12 | manual14<<13 | manual15<<14 | manual16<<15;
	chx_off_on1 = manual17 | manual18<<1 | manual19<<2 | manual20<<3 | manual21<<4 | manual22<<5 | manual23<<6 | manual24<<7
	| manual25<<8 | manual26<<9 | manual27<<10 | manual28<<11 | manual29<<12 | manual30<<13 | manual31<<14 | manual32<<15;
	chx_off_on2 = 0;
	chx_off_on3 = 0;
		
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:1,
		ch0rfpoint:$("#rx0Rfpoint0").val(),
		ch1rfpoint:$("#rx0Rfpoint1").val(),
		ch2rfpoint:$("#rx0Rfpoint2").val(),
		ch3rfpoint:$("#rx0Rfpoint3").val(),
		ch4rfpoint:$("#rx0Rfpoint4").val(),
		ch5rfpoint:$("#rx0Rfpoint5").val(),
		ch6rfpoint:$("#rx0Rfpoint6").val(),
		ch7rfpoint:$("#rx0Rfpoint7").val(),
		ch8rfpoint:$("#rx0Rfpoint8").val(),
		ch9rfpoint:$("#rx0Rfpoint9").val(),
		ch10rfpoint:$("#rx0Rfpoint10").val(),
		ch11rfpoint:$("#rx0Rfpoint11").val(),
		ch12rfpoint:$("#rx0Rfpoint12").val(),
		ch13rfpoint:$("#rx0Rfpoint13").val(),
		ch14rfpoint:$("#rx0Rfpoint14").val(),
		ch15rfpoint:$("#rx0Rfpoint15").val(),
		ch16rfpoint:$("#rx0Rfpoint16").val(),
		ch17rfpoint:$("#rx0Rfpoint17").val(),
		ch18rfpoint:$("#rx0Rfpoint18").val(),
		ch19rfpoint:$("#rx0Rfpoint19").val(),
		ch20rfpoint:$("#rx0Rfpoint20").val(),
		ch21rfpoint:$("#rx0Rfpoint21").val(),
		ch22rfpoint:$("#rx0Rfpoint22").val(),
		ch23rfpoint:$("#rx0Rfpoint23").val(),
		ch24rfpoint:$("#rx0Rfpoint24").val(),
		ch25rfpoint:$("#rx0Rfpoint25").val(),
		ch26rfpoint:$("#rx0Rfpoint26").val(),
		ch27rfpoint:$("#rx0Rfpoint27").val(),
		ch28rfpoint:$("#rx0Rfpoint28").val(),
		ch29rfpoint:$("#rx0Rfpoint29").val(),
		ch30rfpoint:$("#rx0Rfpoint30").val(),
		ch31rfpoint:$("#rx0Rfpoint31").val(),	
		chx_off_on0:chx_off_on0,
		chx_off_on1:chx_off_on1,
		chx_off_on2:chx_off_on2,
		chx_off_on3:chx_off_on3,
		chnumber:$("#chnumber",parent.document).val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
	/*
	//联动
	for(i = 0; i < 32; i++){
		if($("#rx0Rfpoint"+i).val() == 0)
			$("#rx1Rfpoint"+i).val(0);
		else
			$("#rx1Rfpoint"+i).val(parseFloat($("#rx0Rfpoint"+i).val())+10);
	}
		
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:2,
		ch0rfpoint:$("#rx1Rfpoint0").val(),
		ch1rfpoint:$("#rx1Rfpoint1").val(),
		ch2rfpoint:$("#rx1Rfpoint2").val(),
		ch3rfpoint:$("#rx1Rfpoint3").val(),
		ch4rfpoint:$("#rx1Rfpoint4").val(),
		ch5rfpoint:$("#rx1Rfpoint5").val(),
		ch6rfpoint:$("#rx1Rfpoint6").val(),
		ch7rfpoint:$("#rx1Rfpoint7").val(),
		ch8rfpoint:$("#rx1Rfpoint8").val(),
		ch9rfpoint:$("#rx1Rfpoint9").val(),
		ch10rfpoint:$("#rx1Rfpoint10").val(),
		ch11rfpoint:$("#rx1Rfpoint11").val(),
		ch12rfpoint:$("#rx1Rfpoint12").val(),
		ch13rfpoint:$("#rx1Rfpoint13").val(),
		ch14rfpoint:$("#rx1Rfpoint14").val(),
		ch15rfpoint:$("#rx1Rfpoint15").val(),
		ch16rfpoint:$("#rx1Rfpoint16").val(),
		ch17rfpoint:$("#rx1Rfpoint17").val(),
		ch18rfpoint:$("#rx1Rfpoint18").val(),
		ch19rfpoint:$("#rx1Rfpoint19").val(),
		ch20rfpoint:$("#rx1Rfpoint20").val(),
		ch21rfpoint:$("#rx1Rfpoint21").val(),
		ch22rfpoint:$("#rx1Rfpoint22").val(),
		ch23rfpoint:$("#rx1Rfpoint23").val(),
		ch24rfpoint:$("#rx1Rfpoint24").val(),
		ch25rfpoint:$("#rx1Rfpoint25").val(),
		ch26rfpoint:$("#rx1Rfpoint26").val(),
		ch27rfpoint:$("#rx1Rfpoint27").val(),
		ch28rfpoint:$("#rx1Rfpoint28").val(),
		ch29rfpoint:$("#rx1Rfpoint29").val(),
		ch30rfpoint:$("#rx1Rfpoint30").val(),
		ch31rfpoint:$("#rx1Rfpoint31").val(),
		chx_off_on0:chx_off_on0,
		chx_off_on1:chx_off_on1,
		chx_off_on2:chx_off_on2,
		chx_off_on3:chx_off_on3,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
	*/
}
//频点配置
function writeRx1Rfpoint()
{
	manual1=document.getElementById("checkbox_rx1Manual1").checked==true?0:1,
	manual2=document.getElementById("checkbox_rx1Manual2").checked==true?0:1,
	manual3=document.getElementById("checkbox_rx1Manual3").checked==true?0:1,
	manual4=document.getElementById("checkbox_rx1Manual4").checked==true?0:1,
	manual5=document.getElementById("checkbox_rx1Manual5").checked==true?0:1,
	manual6=document.getElementById("checkbox_rx1Manual6").checked==true?0:1,
	manual7=document.getElementById("checkbox_rx1Manual7").checked==true?0:1,
	manual8=document.getElementById("checkbox_rx1Manual8").checked==true?0:1,
	manual9=document.getElementById("checkbox_rx1Manual9").checked==true?0:1,
	manual10=document.getElementById("checkbox_rx1Manual10").checked==true?0:1,
	manual11=document.getElementById("checkbox_rx1Manual11").checked==true?0:1,
	manual12=document.getElementById("checkbox_rx1Manual12").checked==true?0:1,
	manual13=document.getElementById("checkbox_rx1Manual13").checked==true?0:1,
	manual14=document.getElementById("checkbox_rx1Manual14").checked==true?0:1,
	manual15=document.getElementById("checkbox_rx1Manual15").checked==true?0:1,
	manual16=document.getElementById("checkbox_rx1Manual16").checked==true?0:1,
	manual17=document.getElementById("checkbox_rx1Manual17").checked==true?0:1,
	manual18=document.getElementById("checkbox_rx1Manual18").checked==true?0:1,
	manual19=document.getElementById("checkbox_rx1Manual19").checked==true?0:1,
	manual20=document.getElementById("checkbox_rx1Manual20").checked==true?0:1,
	manual21=document.getElementById("checkbox_rx1Manual21").checked==true?0:1,
	manual22=document.getElementById("checkbox_rx1Manual22").checked==true?0:1,
	manual23=document.getElementById("checkbox_rx1Manual23").checked==true?0:1,
	manual24=document.getElementById("checkbox_rx1Manual24").checked==true?0:1,
	manual25=document.getElementById("checkbox_rx1Manual25").checked==true?0:1,
	manual26=document.getElementById("checkbox_rx1Manual26").checked==true?0:1,
	manual27=document.getElementById("checkbox_rx1Manual27").checked==true?0:1,
	manual28=document.getElementById("checkbox_rx1Manual28").checked==true?0:1,
	manual29=document.getElementById("checkbox_rx1Manual29").checked==true?0:1,
	manual30=document.getElementById("checkbox_rx1Manual30").checked==true?0:1,
	manual31=document.getElementById("checkbox_rx1Manual31").checked==true?0:1,
	manual32=document.getElementById("checkbox_rx1Manual32").checked==true?0:1,
	chx_off_on0 = manual1 | manual2<<1 | manual3<<2 | manual4<<3 | manual5<<4 | manual6<<5 | manual7<<6 | manual8<<7
	| manual9<<8 | manual10<<9 | manual11<<10 | manual12<<11 | manual13<<12 | manual14<<13 | manual15<<14 | manual16<<15;
	chx_off_on1 = manual17 | manual18<<1 | manual19<<2 | manual20<<3 | manual21<<4 | manual22<<5 | manual23<<6 | manual24<<7
	| manual25<<8 | manual26<<9 | manual27<<10 | manual28<<11 | manual29<<12 | manual30<<13 | manual31<<14 | manual32<<15;
	chx_off_on2 = 0;
	chx_off_on3 = 0;
		
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:2,
		ch0rfpoint:$("#rx1Rfpoint0").val(),
		ch1rfpoint:$("#rx1Rfpoint1").val(),
		ch2rfpoint:$("#rx1Rfpoint2").val(),
		ch3rfpoint:$("#rx1Rfpoint3").val(),
		ch4rfpoint:$("#rx1Rfpoint4").val(),
		ch5rfpoint:$("#rx1Rfpoint5").val(),
		ch6rfpoint:$("#rx1Rfpoint6").val(),
		ch7rfpoint:$("#rx1Rfpoint7").val(),
		ch8rfpoint:$("#rx1Rfpoint8").val(),
		ch9rfpoint:$("#rx1Rfpoint9").val(),
		ch10rfpoint:$("#rx1Rfpoint10").val(),
		ch11rfpoint:$("#rx1Rfpoint11").val(),
		ch12rfpoint:$("#rx1Rfpoint12").val(),
		ch13rfpoint:$("#rx1Rfpoint13").val(),
		ch14rfpoint:$("#rx1Rfpoint14").val(),
		ch15rfpoint:$("#rx1Rfpoint15").val(),
		ch16rfpoint:$("#rx1Rfpoint16").val(),
		ch17rfpoint:$("#rx1Rfpoint17").val(),
		ch18rfpoint:$("#rx1Rfpoint18").val(),
		ch19rfpoint:$("#rx1Rfpoint19").val(),
		ch20rfpoint:$("#rx1Rfpoint20").val(),
		ch21rfpoint:$("#rx1Rfpoint21").val(),
		ch22rfpoint:$("#rx1Rfpoint22").val(),
		ch23rfpoint:$("#rx1Rfpoint23").val(),
		ch24rfpoint:$("#rx1Rfpoint24").val(),
		ch25rfpoint:$("#rx1Rfpoint25").val(),
		ch26rfpoint:$("#rx1Rfpoint26").val(),
		ch27rfpoint:$("#rx1Rfpoint27").val(),
		ch28rfpoint:$("#rx1Rfpoint28").val(),
		ch29rfpoint:$("#rx1Rfpoint29").val(),
		ch30rfpoint:$("#rx1Rfpoint30").val(),
		ch31rfpoint:$("#rx1Rfpoint31").val(),
		chx_off_on0:chx_off_on0,
		chx_off_on1:chx_off_on1,
		chx_off_on2:chx_off_on2,
		chx_off_on3:chx_off_on3,
		chnumber:$("#chnumber",parent.document).val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
	/*
	//联动
	for(i = 0; i < 32; i++){
		if($("#rx1Rfpoint"+i).val() == 0)
			$("#rx0Rfpoint"+i).val(0);
		else
			$("#rx0Rfpoint"+i).val(parseFloat($("#rx1Rfpoint"+i).val())-10);
	}
	
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:1,
		ch0rfpoint:$("#rx0Rfpoint0").val(),
		ch1rfpoint:$("#rx0Rfpoint1").val(),
		ch2rfpoint:$("#rx0Rfpoint2").val(),
		ch3rfpoint:$("#rx0Rfpoint3").val(),
		ch4rfpoint:$("#rx0Rfpoint4").val(),
		ch5rfpoint:$("#rx0Rfpoint5").val(),
		ch6rfpoint:$("#rx0Rfpoint6").val(),
		ch7rfpoint:$("#rx0Rfpoint7").val(),
		ch8rfpoint:$("#rx0Rfpoint8").val(),
		ch9rfpoint:$("#rx0Rfpoint9").val(),
		ch10rfpoint:$("#rx0Rfpoint10").val(),
		ch11rfpoint:$("#rx0Rfpoint11").val(),
		ch12rfpoint:$("#rx0Rfpoint12").val(),
		ch13rfpoint:$("#rx0Rfpoint13").val(),
		ch14rfpoint:$("#rx0Rfpoint14").val(),
		ch15rfpoint:$("#rx0Rfpoint15").val(),
		ch16rfpoint:$("#rx0Rfpoint16").val(),
		ch17rfpoint:$("#rx0Rfpoint17").val(),
		ch18rfpoint:$("#rx0Rfpoint18").val(),
		ch19rfpoint:$("#rx0Rfpoint19").val(),
		ch20rfpoint:$("#rx0Rfpoint20").val(),
		ch21rfpoint:$("#rx0Rfpoint21").val(),
		ch22rfpoint:$("#rx0Rfpoint22").val(),
		ch23rfpoint:$("#rx0Rfpoint23").val(),
		ch24rfpoint:$("#rx0Rfpoint24").val(),
		ch25rfpoint:$("#rx0Rfpoint25").val(),
		ch26rfpoint:$("#rx0Rfpoint26").val(),
		ch27rfpoint:$("#rx0Rfpoint27").val(),
		ch28rfpoint:$("#rx0Rfpoint28").val(),
		ch29rfpoint:$("#rx0Rfpoint29").val(),
		ch30rfpoint:$("#rx0Rfpoint30").val(),
		ch31rfpoint:$("#rx0Rfpoint31").val(),	
		chx_off_on0:chx_off_on0,
		chx_off_on1:chx_off_on1,
		chx_off_on2:chx_off_on2,
		chx_off_on3:chx_off_on3,
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
	*/
}

function writeRx0Center()
{
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:3,
		center:$("#rx0Center").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
	/*
	//联动
	$("#rx1Center").val(parseFloat($("#rx0Center").val())+10);
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:4,
		center:$("#rx1Center").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
	*/
}

function writeRx1Center()
{
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:4,
		center:$("#rx1Center").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
	/*
	//联动
	$("#rx0Center").val(parseFloat($("#rx1Center").val())-10);
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:3,
		center:$("#rx0Center").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
	*/
}

function writeRx0WorkBandwidth()
{
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:14,
		bandwidth:$("#rx0WorkBandwidth").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}

function writeRx1WorkBandwidth()
{
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:15,
		bandwidth:$("#rx1WorkBandwidth").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}

function readRfpoint()
{
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:5,
	},function(data,status){
		if(status == "success")
		{
			var obj = JSON.parse(data);
			$("#rx0Center").val(obj.rx0center.toFixed(4));
			$("#rx1Center").val(obj.rx1center.toFixed(4));
			$("#rx0WorkBandwidth").val(obj.rx0WorkBandwidth.toFixed(4));
			$("#rx1WorkBandwidth").val(obj.rx1WorkBandwidth.toFixed(4));
			for(x in obj.rfpoint_rx0)
				$("#rx0Rfpoint"+x).val(obj.rfpoint_rx0[x].toFixed(4));
			for(x in obj.rfpoint_rx1)
				$("#rx1Rfpoint"+x).val(obj.rfpoint_rx1[x].toFixed(4));
			document.getElementById("select_rfpoint").selectedIndex = obj.onoff;
			var i = 1;
			for(y in obj.rx0Manual)
			{
				if(obj.rx0Manual[y] == 0)
					document.getElementById("checkbox_rx0Manual"+i++).checked = true;
				else
					document.getElementById("checkbox_rx0Manual"+i++).checked = false;
			}
			var j = 1;
			for(y in obj.rx1Manual)
			{
				if(obj.rx1Manual[y] == 0)
					document.getElementById("checkbox_rx1Manual"+j++).checked = true;
				else
					document.getElementById("checkbox_rx1Manual"+j++).checked = false;
			}
			for(x in obj.iir_rx0)
				$("#rx0IIR"+x).val(obj.iir_rx0[x].toFixed(2));
			for(x in obj.iir_rx1)
				$("#rx1IIR"+x).val(obj.iir_rx1[x].toFixed(2));
			for(x in obj.rx0RfCompVal)
				$("#rx0Ch"+x+"Point").val(obj.rx0RfCompVal[x].toFixed(2));
			for(x in obj.rx1RfCompVal)
				$("#rx1Ch"+x+"Point").val(obj.rx1RfCompVal[x].toFixed(2));
			for(x in obj.rx0Power)
				$("#rx0power"+x).val(obj.rx0Power[x].toFixed(2));
			for(x in obj.rx1Power)
				$("#rx1power"+x).val(obj.rx1Power[x].toFixed(2));
		}
		else alert("error");
	});
}

function writeRfpointSwitch()
{
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:7,
		onoff:document.getElementById("select_rfpoint").selectedIndex,
	},
	function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}

function writeRx0IIR()
{
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:10,
		iir0:$("#rx0IIR0").val(),
		iir1:$("#rx0IIR1").val(),
		iir2:$("#rx0IIR2").val(),
		iir3:$("#rx0IIR3").val(),
		iir4:$("#rx0IIR4").val(),
		iir5:$("#rx0IIR5").val(),
		iir6:$("#rx0IIR6").val(),
		iir7:$("#rx0IIR7").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
	/*
	//联动
	for(i = 0; i < 8; i++)
		$("#rx1IIR"+i).val(parseFloat($("#rx0IIR"+i).val()));
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:11,
		iir0:$("#rx1IIR0").val(),
		iir1:$("#rx1IIR1").val(),
		iir2:$("#rx1IIR2").val(),
		iir3:$("#rx1IIR3").val(),
		iir4:$("#rx1IIR4").val(),
		iir5:$("#rx1IIR5").val(),
		iir6:$("#rx1IIR6").val(),
		iir7:$("#rx1IIR7").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
	*/
}

function writeRx1IIR()
{
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:11,
		iir0:$("#rx1IIR0").val(),
		iir1:$("#rx1IIR1").val(),
		iir2:$("#rx1IIR2").val(),
		iir3:$("#rx1IIR3").val(),
		iir4:$("#rx1IIR4").val(),
		iir5:$("#rx1IIR5").val(),
		iir6:$("#rx1IIR6").val(),
		iir7:$("#rx1IIR7").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
	/*
	//联动
	for(i = 0; i < 8; i++)
		$("#rx0IIR"+i).val(parseFloat($("#rx1IIR"+i).val()));
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:10,
		iir0:$("#rx0IIR0").val(),
		iir1:$("#rx0IIR1").val(),
		iir2:$("#rx0IIR2").val(),
		iir3:$("#rx0IIR3").val(),
		iir4:$("#rx0IIR4").val(),
		iir5:$("#rx0IIR5").val(),
		iir6:$("#rx0IIR6").val(),
		iir7:$("#rx0IIR7").val(),
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
	*/
}

function writeRx0ChPointComp()
{
	var chpoint = new Array();
	for(i = 0; i < 32; i++)
		chpoint[i] = parseFloat($("#rx0Ch"+i+"Point").val());
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:12,
		rf1compval:chpoint[0],	
		rf2compval:chpoint[1],	
		rf3compval:chpoint[2],	
		rf4compval:chpoint[3],	
		rf5compval:chpoint[4],	
		rf6compval:chpoint[5],	
		rf7compval:chpoint[6],	
		rf8compval:chpoint[7],	
		rf9compval:chpoint[8],	
		rf10compval:chpoint[9],	
		rf11compval:chpoint[10],	
		rf12compval:chpoint[11],	
		rf13compval:chpoint[12],	
		rf14compval:chpoint[13],	
		rf15compval:chpoint[14],	
		rf16compval:chpoint[15],	
		rf17compval:chpoint[16],	
		rf18compval:chpoint[17],	
		rf19compval:chpoint[18],	
		rf20compval:chpoint[19],	
		rf21compval:chpoint[20],	
		rf22compval:chpoint[21],	
		rf23compval:chpoint[22],	
		rf24compval:chpoint[23],
		rf25compval:chpoint[24],	
		rf26compval:chpoint[25],	
		rf27compval:chpoint[26],	
		rf28compval:chpoint[27],	
		rf29compval:chpoint[28],	
		rf30compval:chpoint[29],	
		rf31compval:chpoint[30],	
		rf32compval:chpoint[31],
	},function(data,status){
		if(status == "success")
			LogDebug(LogMsgType.Normal,data);
		else alert("error");
	});
}

function writeRx1ChPointComp()
{
	var chpoint = new Array();
	for(i = 0; i < 32; i++)
		chpoint[i] = parseFloat($("#rx1Ch"+i+"Point").val());
	$.post("/cgi-bin/rfpoint.cgi",{
		cgiNumber:13,
		rf1compval:chpoint[0],	
		rf2compval:chpoint[1],	
		rf3compval:chpoint[2],	
		rf4compval:chpoint[3],	
		rf5compval:chpoint[4],	
		rf6compval:chpoint[5],	
		rf7compval:chpoint[6],	
		rf8compval:chpoint[7],	
		rf9compval:chpoint[8],	
		rf10compval:chpoint[9],	
		rf11compval:chpoint[10],	
		rf12compval:chpoint[11],	
		rf13compval:chpoint[12],	
		rf14compval:chpoint[13],	
		rf15compval:chpoint[14],	
		rf16compval:chpoint[15],	
		rf17compval:chpoint[16],	
		rf18compval:chpoint[17],	
		rf19compval:chpoint[18],	
		rf20compval:chpoint[19],	
		rf21compval:chpoint[20],	
		rf22compval:chpoint[21],	
		rf23compval:chpoint[22],	
		rf24compval:chpoint[23],
		rf25compval:chpoint[24],	
		rf26compval:chpoint[25],	
		rf27compval:chpoint[26],	
		rf28compval:chpoint[27],	
		rf29compval:chpoint[28],	
		rf30compval:chpoint[29],	
		rf31compval:chpoint[30],	
		rf32compval:chpoint[31],
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
	goindex();
	readRfpoint();
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
