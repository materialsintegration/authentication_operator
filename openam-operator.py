#!/usr/local/python2.7/bin/python
# -*- coding: utf-8 -*-

'''
OpenAM認証用ライブラリ
'''

import sys, os
import time
import json
import datetime
import codecs
import requests
import urllib
import subprocess
import base64
if sys.version_info[0] <= 2:
    import ConfigParser
    from urlparse import urlparse
else:
    import configparser
    from urllib.parse import urlparse, quote as urlquote

def openam_post(resturl, payload=None, headers=None):
    '''
    OpenAMのRESTAPIへpostを実行する
    @param resturl (string) : RESTAPIのエンドポイント
    @param json (json)
    @param headers (dict) : ヘッダー情報
    @retval bool, response(dict/json)
    '''

    session = requests.Session()
    
    result = session.post(resturl, json=payload, headers=headers)

    #print("response of post = %s"%result.text)

    if result.status_code != 200:
        return False, result

    return True, result

def openam_get(resturl, payload=None, headers=None):
    '''
    OpenAMのRESTAPIへgetを実行する
    @param resturl (string) : RESTAPIのエンドポイント
    @param json (json)
    @param headers (dict) : ヘッダー情報
    @retval bool, response(dict/json)
    '''

    session = requests.Session()
    
    result = session.get(resturl, data=payload, headers=headers)

    if result.status_code != 200:
        return False, result

    return True, result

def openam_authenticate(server, user_name, user_password, realm="misystem"):
    '''
    serverの指す認証システムへ認証を実行する
    @param server(string): "https://u-tokyo.mintsys.jp"などのURL
    @param user_name(string)
    @param user_password(string)
    @retval bool, response(dict)
    '''

    if user_name == "" or user_name is None:
        return False, "no username"
    if user_password == "" or user_password is None:
        return False, "no user password"
    if server == "" or server is None:
        return False, "no server name or invalid server name"

    headers = {"X-OpenAM-Username": user_name,
               "X-OpenAM-Password": user_password,
               "Content-Type": "application/json"}

    weburl = "https://%s/sso/json/authenticate?realm=%s"%(server, realm)

    ret, result = openam_post(weburl, payload=None, headers=headers)

    if ret is True:
        response = result.json()
        print("Response = {")
        for item in response:
            print("    key = %s / value = %s"%(item, response[item]))

        print("}")

    return ret, result

def openam_getcode(server, token, realm="misystem"):
    '''
    serverの指す認証システムへ取得したtokenでコードを得る
    @param server(string):
    @param token(string)
    @retval bool, code(string) : Falseの場合はbody
    '''

    print("------ getting code ------")
    headers = {"Cookie":"iPlanetDirectoryPro=%s"%token,
               "Content-Type": "application/x-www-form-urlencoded",
               "Cache-Control": "no-cache"}

    jdata = {"response_type":"id_token",
            "scope":"openid profile mi-user-id Mi-User-Id qualified email",
            "client_id":"sipauthApp",
            "redirect_uri":"https://%s"%server,
            "save_consent":"1",
            "decision":"Allow"}
    #        "nonce":"ZZZZZZ", "state":"ZZZZZZ"}

    #data = urlparse("response_type=id_token token&scope=openid&client_id=sipauthApp&redirect_uri=https://%s&save_consent=1&decision=Allow&nonce=ZZZZZZZ&state=ZZZZZZ"%server)
    data = urlparse("response_type=code&scope=openid profile qualified email&client_id=sipauthApp&redirect_uri=https://%s&save_consent=1&decision=Allow&nonce=ZZZZZZZ&state=ZZZZZZ"%server)

    #weburl = "https://%s/sso/oauth2/authorize?realm=%s"%(server, realm)
    weburl = "https://%s/sso/oauth2/%s/authorize?%s"%(server, realm, data.geturl())
    #weburl = "https://%s/sso/oauth2/%s/authorize"%(server, realm)

    # simulate this function by curl command for debug
    print("curl command")
    print("curl -X POST \\")
    print('  -H "Cookie:%s" \\'%(headers["Cookie"]))
    print('  -H "Content-Type:%s" \\'%(headers["Content-Type"]))
    print('  -H "Cache-Control: %s" \\'%(headers["Cache-Control"]))
    print("  -d '%s' \\"%data.geturl().replace(" ", "%20"))
    print("  -k -v https://%s/sso/oauth2/%s/authorize"%(server, realm))

    #ret, result = openam_post(weburl, json=jdata, headers=headers)
    ret, result = openam_post(weburl, payload=None, headers=headers)
    if ret is False:
        message = result.text.split("\n")
        print("url     = :",weburl)
        print("headers = :",headers)
        print("code =    :",result.status_code)
        print("body =    :"),
        for item in message:
            print("%s"%item)
        return ret, result.text

    #for item in result.__dict__:
    #    if item == "request":
    #        print("key = %s / value = %s"%(item, result.__dict__[item]))
    #        for req_item in result.__dict__[item].__dict__:
    #            print("  key = %s / value = %s"%(req_item, result.__dict__[item].__dict__[req_item]))
    #    else:
    #        print("key = %s / value = %s"%(item, result.__dict__[item]))
    #print("url = %s"%urlparse(urllib.unquote(result.url)))
    print("url = %s"%result.url)
    items = urllib.unquote(result.url).split('&')
    #print('item no 2 after urlparse and split by &(%s)'%items[2])
    item = items[2].split("code=")[1]
    print("code is %s"%item)
    return True, item

def openam_getaccess_token2(server, token, realm="misystem"):
    '''
    serverの指す認証システムへ取得したtokenでaccess_token他を得る
    requests.Sessionで、うまくいかないので、curlを使用中
    @param server(string):
    @param token(string)
    @retval bool, code(string) : Falseの場合はbody
    '''

    print("------ getting code and access_token ------")
    headers = {"Cookie":"iPlanetDirectoryPro=%s"%token,
               "Content-Type": "application/x-www-form-urlencoded",
               "Cache-Control": "no-cache"}

    data = urlparse("response_type=id_token token&scope=openid&client_id=sipauthApp&redirect_uri=https://%s&save_consent=1&decision=Allow&nonce=ZZZZZZZ&state=ZZZZZZ"%server)

    weburl = "https://%s/sso/oauth2/%s/authorize"%(server, realm)

    # simulate this function by curl command for debug
    #print("curl command")
    #print("curl -X POST \\")
    #print('  -H "Cookie:%s" \\'%(headers["Cookie"]))
    #print('  -H "Content-Type:%s" \\'%(headers["Content-Type"]))
    #print('  -H "Cache-Control: %s" \\'%(headers["Cache-Control"]))
    #print("  -d '%s' \\"%data.geturl().replace(" ", "%20"))
    #print("  -k -v https://%s/sso/oauth2/%s/authorize"%(server, realm))

    # construct command line for subprocess
    curl_cmd = 'curl -X POST -H "Cookie:%s" -H "Content-Type:%s" -H "Cache-Control: %s" -d "%s" -k -v https://%s/sso/oauth2/%s/authorize'%(headers["Cookie"], headers["Content-Type"], headers["Cache-Control"], data.geturl().replace(" ", "%20"), server, realm)

    print("cmd = %s"%curl_cmd)
    proc = subprocess.Popen(curl_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Location:を含んでいるresponseを取得
    location_response = ""
    while True:
        aline = proc.stdout.readline()
        items = aline.split()
        if not aline and proc.poll() is not None:
            break
        if len(items) == 0:
            continue
        else:
            #print"items = %s"%items
            pass
        if len(items) != 1 and items[1] == "Location:":
            location_response = items

    #print("response with Location: %s", location_response[2])
    item1 = location_response[2].split("#")
    #print("Location = %s"%item1)
    item2 = item1[1].split("&")
    #print("access_token = %s"%item2[0])

    return True, item2

def openam_getaccess_token(server, code, realm="misystem"):
    '''
    serverの指す認証システムへ取得したcodeでアクセストークンを得る
    @param server(string):
    @param code(string)
    @retval bool, access_token(string) Falseの場合はbody
    '''

    print("------ getting access_token ------")
    headers = {"Cache-Control": "no-cache",
               "Content-Type": "application/x-www-form-urlencoded",
               #"grant_type":"authorization_code",
               #"code":"%s"%code,
               #"redirect_uri":"https://%s"%server,
               "Authorization": "Basic %s"%base64.b64encode("sipauthApp:P@ssw0rd")}
    jdata = {'grant_type':'authorization_code',
             'code':'%s'%code,
             'redirect_uri':'https://%s'%server}

    data = urlparse("grant_type=authorization_code&code=%s&redirect_uri=https://%s"%(code, server))

    #weburl = "https://%s/sso/oauth2/%s/access_token"%(server, realm)
    weburl = "https://%s/sso/oauth2/%s/access_token?%s"%(server, realm, data.geturl())

    # simulate this function by curl command for debug
    print("curl command")
    print("curl -X POST \\")
    print('  -H "Cache-Control: %s" \\'%headers["Cache-Control"])
    print('  -H "Authorization: %s" \\'%headers["Authorization"])
    print("  -d '%s' \\"%data.geturl().replace(" ", "%20"))
    print("  -k -v https://%s/sso/oauth2/%s/access_token"%(server, realm))

    #ret, result = openam_post(weburl, headers=headers, payload=jdata)
    ret, result = openam_post(weburl, payload=None, headers=headers)
    if ret is False:
        for item in result.__dict__:
            if item == "request":
                print("key = %s / value = %s"%(item, result.__dict__[item]))
                for req_item in result.__dict__[item].__dict__:
                    print("  key = %s / value = %s"%(req_item, result.__dict__[item].__dict__[req_item]))
            else:
                print("key = %s / value = %s"%(item, result.__dict__[item]))
        return ret, result
    else:
        response = result.json()
        print("Response = {")
        for item in response:
            print("    key = %s / value = %s"%(item, response[item]))

        print("}")
    
        return ret, result.json()["access_token"]

def openam_get_userinfo(server, access_token, realm="misystem"):
    '''
    serverの指す認証システムへ取得したaccess_tokenでユーザー情報を得る
    @param server(string):
    @param access_token(string)
    @param realm(string)
    @retval bool, access_token(string) Falseの場合はbody
    '''

    print("------ getting user informations ------")
    headers = {"Authorization":"Bearer %s"%access_token}

    weburl = "https://%s/sso/oauth2/%s/userinfo"%(server, realm)
    #weburl = "https://%s/sso/oauth2/userinfo"%(server)

    # simulate this function by curl command for debug
    print("curl command")
    print("curl -X POST \\")
    print('  -H "Authorization: %s" \\'%(headers["Authorization"]))
    print("  -d 'claims=mi-api-token&scope=mi-api-token' \\")
    print("  -k -v https://%s/sso/oauth2/%s/userinfo"%(server, realm))

    ret, result = openam_get(weburl, payload={"claims":"mi-api-token"}, headers=headers)
    if ret is False:
        for item in result.__dict__:
            if item == "raw":
                print("  key = %s / value = %s"%(item, result.__dict__[item].read("_content")))
            elif item == "request":
                print("key = %s / value = %s"%(item, result.__dict__[item]))
                for req_item in result.__dict__[item].__dict__:
                    print("  key = %s / value = %s"%(req_item, result.__dict__[item].__dict__[req_item]))
            else:
                print("key = %s / value = %s"%(item, result.__dict__[item]))
        return ret, result
    else:
        print("Response = {")
        for item in result.json():
            print("    key = %s / value = %s"%(item, result.json()[item]))

        print("}")
        return ret, result.json()

def main():
    '''
    コマンドラインからの実行開始点
    '''

    params_len = len(sys.argv)
    if params_len < 4:
       print "python authentication-operater.py <server> <user name> <password>"

    server = sys.argv[1]
    user_name = sys.argv[2]
    user_passwd = sys.argv[3]

    # 認証

    ret, result = openam_authenticate(server, user_name, user_passwd)
    if ret is False:
        print("response = ", result)
        sys.exit(1)
    else:
        #print("response = %s"%result)
        pass

    print("認証OK")
    # code取得
    token = result.json()["tokenId"]
    ret, result = openam_getcode(server, token)
    #if ret is False:
    #    print("response = ", result)
    #else:
    #    print("response = %s"%result.text)
    #    pass

    # access_token取得
    code = result
    ret, result = openam_getaccess_token(server, code)

    #ret, result = openam_getaccess_token2(server, token)
    #access_token = result[0].split("=")[1]
    access_token = result
    print("access_token is %s"%access_token)

    # userinfo取得
    ret, result = openam_get_userinfo(server, access_token)

if __name__ == '__main__':

    main()
