function txtClear()
{
	$("#textarea_Debug").html("");
	$("#textarea_UiProtocol").html("");
}

var LogMsgType = {
	Incoming:0,
	Outgoing:1,
	Normal:2,
	Warning:3,
	Error:4,
};
var LogMsgTypeColor = ["blue","green","black","orange","red"];

function LogDebug(msgType,msg)
{
	var myDate = new Date();
	var mytime = myDate.toLocaleTimeString();
	var ms = myDate.getMilliseconds();
	if(ms < 100 && ms >= 10)
		mytime += (":0" + ms + " ");
	if(ms < 10)
		mytime += (":00" + ms + " ");
	if(ms >= 100)
		mytime += (":" + ms + " ");

	var font = document.createElement("font");
	var textarea = document.getElementById("textarea_Debug");
	font.color = LogMsgTypeColor[msgType];
	font.innerText = mytime+msg+"\r\n";
	textarea.appendChild(font);
	textarea.scrollTop = textarea.scrollHeight;
}

function LogUiProtocol(msgType,msg)
{
	var myDate = new Date();
	var mytime = myDate.toLocaleTimeString();
	var ms = myDate.getMilliseconds();
	if(ms < 100 && ms >= 10)
		mytime += (":0" + ms + " ");
	if(ms < 10)
		mytime += (":00" + ms + " ");
	if(ms >= 100)
		mytime += (":" + ms + " ");
	var text = document.createElement("font");
	text.color = LogMsgTypeColor[msgType];
	text.innerText = mytime+msg+"\r\n";
	var textarea = document.getElementById("textarea_UiProtocol");
	textarea.appendChild(text);
	textarea.scrollTop = textarea.scrollHeight;
}

function LogUpdate(msgType,msg)
{
	var myDate = new Date();
	var mytime = myDate.toLocaleTimeString();
	var ms = myDate.getMilliseconds();
	if(ms < 100 && ms >= 10)
		mytime += (":0" + ms + " ");
	if(ms < 10)
		mytime += (":00" + ms + " ");
	if(ms >= 100)
		mytime += (":" + ms + " ");
	var text = document.createElement("font");
	text.color = LogMsgTypeColor[msgType];
	text.innerText = mytime+msg+"\r\n";
	var textarea = document.getElementById("textarea_update");
	textarea.appendChild(text);
	textarea.scrollTop = textarea.scrollHeight;
}

//进行Ini文件内容的解析，解析成Json格式
function ParseINIString(data)
{
    //利用正则表达式进行ini文件每行数据的匹配
    var regex = {
        section: /^\s*\[\s*([^\]]*)\s*\]\s*$/,  
        param: /^\s*([\w\.\-\_]+)\s*=\s*(.*?)\s*$/,
        comment: /^\s*;.*$/
    }; 
    var JsonValue = {}; 
    var lines = new Array();
    lines = data.split(/\r\n|\r|\n/);
    //将字符串进行根据回车拆分为字符串数组  
    var section = null;
    //对字符串数组进行正则表达式匹配，来组装Json对象
    var iArraySize = lines.length;
    for(var i = 0; i < iArraySize; ++i) 
    {
         line = lines[i];
        if(regex.comment.test(line))
        {
            //如果为注释的话，不进行操作
        }else if(regex.param.test(line))
        {
            var match = line.match(regex.param);
            if(section){
                JsonValue[section][match[1]] = match[2];
            }else{
                JsonValue[match[1]] = match[2];
            }
        }else if(regex.section.test(line))
        {
            var match = line.match(regex.section);
            JsonValue[match[1]] = {};
            section = match[1];
        }else if(line.length == 0 && section)
        {
            section = null;
        }
    }
    return JsonValue;
}

//根据Json对象和key值获取相关Ini文件中的值 
function GetValueFromJsonByKey(JsonValue, key)
{
    var value = null; //返回值
    var keyValue = null; //临时存储当前key值
    var strKeyArray = new Array();
    strKeyArray = key.split('.');  //支持传入的key值样式: Key1.key2.key3
    var iKeyCount  = strKeyArray.length;
    if(iKeyCount > 0)
    {
        keyValue = strKeyArray[0];
        value = JsonValue[keyValue];
    }
    for(var iIndex = 1; iIndex < iKeyCount; ++iIndex)
    {
        keyValue = strKeyArray[iIndex];
        value = value[keyValue];
    }
    return value;
}

//输出补0
function PreFixInterge(num,n){  
	//num代表传入的数字，n代表要保留的字符的长度  
	return (Array(n).join(0)+num).slice(-n);  
}

