#encoding: utf - 8

import urllib2 # 请求模块
import urllib  # 格式化请求参数模块
import json  # json模块
import re  # 正则模块
import execjs  # 运行本地js代码

baidu_sign = baidu_token = baidu_set_cookies = None

# 查询翻译结果
def findTranslateResult(query, from_lang, to_lang):
    global baidu_sign, baidu_token, baidu_set_cookies
    if baidu_set_cookies == None or baidu_sign == None:
        gtkResponse = urllib2.urlopen("http://fanyi.baidu.com/?aldtype=16047")
        baidu_set_cookies = gtkResponse.info().get("Set-Cookie")
        infoStr = gtkResponse.read().decode("utf-8")
        gtkRe = re.search(r";window.gtk = '([\d\.]+)';", infoStr)
        gtk = gtkRe.group(1)
        baidu_sign = _calcSign(query, gtk)
    cookie = baidu_set_cookies.split('domain=.baidu.com,')[1]

    # 必须要重新访问获取token
    if baidu_token == None:
        tokenHeaders = {}
        tokenHeaders["Cookie"] = cookie
        tokenRequest = urllib2.Request("http://fanyi.baidu.com/?aldtype=16047", None, tokenHeaders)
        tokenResponse = urllib2.urlopen(tokenRequest)
        infoStr = tokenResponse.read().decode("utf-8")
        tokenRe = re.search(r"token: '([\w]+)',", infoStr)
        baidu_token = tokenRe.group(1)
    url = "https://fanyi.baidu.com/v2transapi"

    headers = {}
    headers["Cookie"] = cookie
    data = {}
    data["from"] = from_lang
    data["to"] = to_lang
    data["query"] = query
    data["transtype"] = "realtime"
    data["simple_means_flag"] = "3"
    data["sign"] = baidu_sign
    data["token"] = baidu_token
    data = urllib.urlencode(data).encode("utf-8")
    req = urllib2.Request(url = url, data = data, headers = headers)
    response = urllib2.urlopen(req)
    all_text = response.read().decode("utf-8")
    jsonResult = json.loads(all_text)
    result = jsonResult['trans_result']['data'][0]['dst']
    return result


# 计算sign
def _calcSign(query, gtk):
    with open("sign.js", "r") as f:
        jsStr = f.read()
    ctx = execjs.compile(jsStr)
    result = ctx.call("e", query, gtk)
    return result


if __name__ == "__main__":
    print(findTranslateResult("hello",'en','spa'))
