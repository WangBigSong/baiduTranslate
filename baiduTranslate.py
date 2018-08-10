import urllib.request as request #请求模块
import urllib.parse as parse #格式化请求参数模块
import json #json模块
import re #正则模块
import execjs #运行本地js代码

sign = token = set_cookies =  None
#查询类型
def _findType(query):
    url = 'http://fanyi.baidu.com/langdetect'
    data = {}
    data["query"] = query
    data = parse.urlencode(data).encode("utf-8")
    result = None
    with request.urlopen(url,data) as response:
        result = response.read().decode("utf-8")
    jsonResult = json.loads(result)
    return jsonResult.get("lan")

#查询翻译结果
def findTranslateResult(query):
    global sign,token,set_cookies
    if set_cookies == None or sign == None:
        with request.urlopen("http://fanyi.baidu.com/?aldtype=16047") as gtkResponse:
            set_cookies = gtkResponse.info().get_all("Set-Cookie")
            infoStr = gtkResponse.read().decode("utf-8")
            gtkRe = re.search(r";window.gtk = '([\d\.]+)';",infoStr)
            gtk = gtkRe.group(1)
            sign = _calcSign(query,gtk)
    cookie = ""
    for each in set_cookies:
        if "BAIDUID" in each:
            cookie = each
            break
    #必须要重新访问获取token
    if token == None:
         tokenHeaders = {}
         tokenHeaders["Cookie"] = cookie
         tokenRequest = request.Request("http://fanyi.baidu.com/?aldtype=16047",None,tokenHeaders)
         with request.urlopen(tokenRequest) as tokenResponse:
             infoStr = tokenResponse.read().decode("utf-8")
             tokenRe = re.search(r"token: '([\w]+)',",infoStr)
             token = tokenRe.group(1)
    fromLan = _findType(query)
    url="http://fanyi.baidu.com/v2transapi"
    
    headers = {}
    headers["Cookie"] = cookie
    data = {}
    data["from"] = fromLan
    data["to"] = "en"
    data["query"] = query
    data["transtype"] = "translang"
    data["simple_means_flag"] = "3"
    data["sign"] = sign
    token = token
    data["token"] = token
    data = parse.urlencode(data).encode("utf-8")
    req = request.Request(url,data,headers)
    result = None
    with request.urlopen(req) as response:
        result = response.read().decode("utf-8")
    jsonResult = json.loads(result)
    jsonResult = jsonResult["dict_result"]["simple_means"]["symbols"][0]["parts"][0]["means"]
    resultList = [];
    for each in jsonResult:
        resultList.append(each["text"])
    return resultList

#计算sign
def _calcSign(query,gtk):
    with open("sign.js","r",encoding="utf-8") as f:
        jsStr  = f.read()
    ctx = execjs.compile(jsStr)
    result = ctx.call("e",query,gtk)
    return result;
    
if __name__ == "__main__":
    print(findTranslateResult("推送"))
       
        

    
