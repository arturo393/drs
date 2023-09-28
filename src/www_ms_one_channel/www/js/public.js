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

//����Ini�ļ����ݵĽ�����������Json��ʽ
function ParseINIString(data)
{
    //����������ʽ����ini�ļ�ÿ�����ݵ�ƥ��
    var regex = {
        section: /^\s*\[\s*([^\]]*)\s*\]\s*$/,  
        param: /^\s*([\w\.\-\_]+)\s*=\s*(.*?)\s*$/,
        comment: /^\s*;.*$/
    }; 
    var JsonValue = {}; 
    var lines = new Array();
    lines = data.split(/\r\n|\r|\n/);
    //���ַ������и��ݻس����Ϊ�ַ�������  
    var section = null;
    //���ַ����������������ʽƥ�䣬����װJson����
    var iArraySize = lines.length;
    for(var i = 0; i < iArraySize; ++i) 
    {
         line = lines[i];
        if(regex.comment.test(line))
        {
            //���Ϊע�͵Ļ��������в���
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

//����Json�����keyֵ��ȡ���Ini�ļ��е�ֵ 
function GetValueFromJsonByKey(JsonValue, key)
{
    var value = null; //����ֵ
    var keyValue = null; //��ʱ�洢��ǰkeyֵ
    var strKeyArray = new Array();
    strKeyArray = key.split('.');  //֧�ִ����keyֵ��ʽ: Key1.key2.key3
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

//�����0
function PreFixInterge(num,n){  
	//num����������֣�n����Ҫ�������ַ��ĳ���  
	return (Array(n).join(0)+num).slice(-n);  
}

