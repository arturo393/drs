function button_Update()
{
	$("#file_Update").click();

	$.post("/cgi-bin/module.cgi",{
		cgiNumber:36,
	},function(data,status){
		if(status == "success"){
			//LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function updateFileName()
{
	$(":button").attr('disabled',true);
	$("a").css("pointer-events","none");
	var block = 10*1024; // 每次读取
	var file;// 当前文件对象
	var fileLoaded;// 当前已读取大小
	var fileSize;// 文件总大小
	var blob;

	file = document.getElementById("file_Update").files[0];
	$("#span_fileName").text(file.name);
	fileLoaded = 0;
	fileSize = file.size;
	
	var index = 0;
	if((file.name.lastIndexOf("boot")) != -1)
		index = 2;
	else if((file.name.lastIndexOf("uimage")) != -1)
		index = 3;
	else if((file.name.lastIndexOf("rootfs")) != -1)
		index = 4;
	else if((file.name.lastIndexOf("tar")) != -1)
		index = 5;
	else if((file.name.lastIndexOf("bin")) != -1 && fileSize < 3900000)
		index = 6;
	else if((file.name.lastIndexOf("bin")) != -1 && fileSize > 3900000)
		index = 7;
		
	if(index == 5 || index == 6)
		block = 200*1024;//200K
	else if(index == 4 || index == 7)
		block = 500*1024;//500K
	else if(index == 3)
		block = 100*1024;//100K
		
	if(window.FileReader)//检测，ie10及以上支持
	{
		LogDebug(LogMsgType.Normal,"FileReader supported by your browser!");
		var reader = new FileReader();
		reader.onerror = function(){
			$("#progressBar").val(0);
		}
		// 每个blob读取完毕时调用
		reader.onload = function(e) {
			var bb = new Blob([this.result]);
			var xhr = new XMLHttpRequest();
			xhr.open("POST", "/cgi-bin/uploadFileReader.cgi", false);//cgiTarget
			xhr.send(bb);
		   	fileLoaded += e.loaded;
			var percent = fileLoaded / fileSize;
			$("#progressBar").val(Math.ceil(percent * 100));
			LogUpdate(LogMsgType.Normal,"Upload Progress："+(percent*100).toFixed(2)+"%");
			if(percent < 1)  {
				// 继续读取下一块
				if(file.webkitSlice) {
					blob = file.webkitSlice(fileLoaded, fileLoaded + block + 1);
				} else if(file.mozSlice) {
					blob = file.mozSlice(fileLoaded, fileLoaded + block + 1);
				} else if(file.slice) {
					blob = file.slice(fileLoaded, fileLoaded + block + 1);
				} else {
					LogDebug(LogMsgType.Error,'Unsupported section！');
					return false;
				}
				reader.readAsArrayBuffer(blob);
			} else {
				// 结束
				percent = 1;
				$("#progressBar").val(0);
				if(index == 2)
					LogDebug(LogMsgType.Normal,"Start uploading uboot......");
				else if(index == 3)
					LogDebug(LogMsgType.Normal,"start uploading kernel......");
				else if(index == 4)
					LogDebug(LogMsgType.Normal,"start uploading rootfs......");
				else if(index == 5)
					LogDebug(LogMsgType.Normal,"start uploading app......");
				else if(index == 6 || index == 7)
					LogDebug(LogMsgType.Normal,"start uploading fpga......");
				LogDebug(LogMsgType.Normal,"Uploading，be aware to operating!");
				LogDebug(LogMsgType.Normal,"wait for 5 minite for completing uploading,then operate next！");
				//再提交一个请求升级
				$.post("/cgi-bin/module.cgi",{
					cgiNumber:index,
				},
				function(data,status){
					if(status == "success")
					{
						var obj = JSON.parse(data);
						if(obj.ret == 0)
						{
							if(index == 2)
								LogDebug(LogMsgType.Normal,"complete uploading uboot");
							else if(index == 3)
								LogDebug(LogMsgType.Normal,"complete uploading kernel");
							else if(index == 4)
								LogDebug(LogMsgType.Normal,"complete uploading rootfs");
							else if(index == 5)
								LogDebug(LogMsgType.Normal,"complete uploading app");
							else if(index == 6 || index == 7)
								LogDebug(LogMsgType.Normal,"complete uploading fpga");
						}
						else
							LogDebug(LogMsgType.Normal,"uploading failure！！！"+data);
						
						LogDebug(LogMsgType.Normal,"restarting device！wait for 2 min...");
						$.post("/cgi-bin/module.cgi",{
							cgiNumber:8,
						},
						function(data,status){
							LogDebug(LogMsgType.Normal,data);
						});
					}			
					else 
						LogDebug(LogMsgType.Normal,"uploading failure！");
					
					$("#file_Update").val("");
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
			LogDebug(LogMsgType.Error,'unsupported section！');
			return false;
		}
		reader.readAsArrayBuffer(blob);
	}
	else
	{
		LogDebug(LogMsgType.Normal,"FileReader not supported by your browser!");
	}
}

function readModule()
{
	$.post("/cgi-bin/module.cgi",{
		cgiNumber:22,
	},function(data,status){
		if(status == "success"){
			var obj = JSON.parse(data);
			$("#textbox_ip0").val(obj.ip1);
			$("#textbox_ip1").val(obj.ip2);
			$("#textbox_ip2").val(obj.ip3);
			$("#textbox_ip3").val(obj.ip4);
			$("#textbox_id").val(obj.id);
			$("#textbox_baudrate_485").val(obj.baudrate485);
			$("#textbox_monitor_ip").val(obj.monitorip);
			$("#textbox_monitor_port").val(obj.monitorport);
		}
		else alert("error");
	});
}

function write_baudrate()
{
	$.post("/cgi-bin/module.cgi",{
		cgiNumber:34,
		baudrate485:$("#textbox_baudrate_485").val(),
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function writeID()
{
	$.post("/cgi-bin/module.cgi",{
		cgiNumber:33,
		id:$("#textbox_id").val(),
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function saveFacCnf()
{
	$.post("/cgi-bin/module.cgi",{
		cgiNumber:26,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function recoverFacCnf()
{
	LogDebug(LogMsgType.Normal,"recover device successful and restaring,please wait for 2 min！");
	$.post("/cgi-bin/module.cgi",{
		cgiNumber:20,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function recoverSameCnf()
{
	LogDebug(LogMsgType.Normal,"recover device successful and restaring,please wait for 2 min！！");
	$.post("/cgi-bin/module.cgi",{
		cgiNumber:21,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function writeIP()
{
	for(i=0;i<4;i++)
	{
		if($("#textbox_ip"+i).val()=="") 
		{
			LogDebug(LogMsgType.Error,"input IP");
			return ;
		}
		var b = /^[0-9]*$/g;
		if(false == b.test($("#textbox_ip"+i).val()))
		{
			LogDebug(LogMsgType.Error,"IP value should be:0~255");
			return ;
		}
		var n = parseInt($("#textbox_ip"+i).val(),10);
		if(isNaN(n) || n<0 || n>255)
		{
			LogDebug(LogMsgType.Error,"IP value should be:0~255");
			return ;
		}
	}
	$.post("/cgi-bin/module.cgi",{
		cgiNumber:19,
		ip1:$("#textbox_ip0").val(),
		ip2:$("#textbox_ip1").val(),
		ip3:$("#textbox_ip2").val(),
		ip4:$("#textbox_ip3").val(),
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

function writeMonitor()
{
	$.post("/cgi-bin/module.cgi",{
		cgiNumber:35,
		monitorip:$("#textbox_monitor_ip").val(),
		monitorport:$("#textbox_monitor_port").val(),
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}

function sysreboot()
{
	$.post("/cgi-bin/module.cgi",{
		cgiNumber:8,
	},function(data,status){
		if(status == "success"){
			LogDebug(LogMsgType.Normal,data);
		}
		else alert("error");
	});
}


window.onload = function(){
	var username=$("#adminbutton",parent.document).text();
	if(username=="Enter Admin"){
		
		$("#appuphtml").attr("style","display: none");
		$("#returnhtml").attr("style","display: none");
	
		
	}else{
		$("#appuphtml").removeAttr("style");
		$("#returnhtml").removeAttr("style");

	}
    goindex();
	readModule();
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

