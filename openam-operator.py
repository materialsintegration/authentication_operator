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
if sys.version_info[0] <= 2:
    import ConfigParser
    from urlparse import urlparse
else:
    import configparser
    from urllib.parse import urlparse, quote as urlquote

def openam_post(resturl, json=None, headers=None):
    '''
    OpenAMのRESTAPIへpostを実行する
    @param resturl (string) : RESTAPIのエンドポイント
    @param json (json)
    @param headers (dict) : ヘッダー情報
    @retval bool, response(dict/json)
    '''

    session = requests.Session()
    
    result = session.post(resturl, json=json, headers=headers)

    #print("response of post = %s"%result.text)

    if result.status_code != 200:
        return False, result

    return True, result

def openam_get(resturl, json=None, headers=None):
    '''
    OpenAMのRESTAPIへgetを実行する
    @param resturl (string) : RESTAPIのエンドポイント
    @param json (json)
    @param headers (dict) : ヘッダー情報
    @retval bool, response(dict/json)
    '''

    session = requests.Session()
    
    result = session.get(resturl, json=json, headers=headers)

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

    ret, result = openam_post(weburl, json=None, headers=headers)

    return ret, result

def openam_getcode(server, token, realm="misystem"):
    '''
    serverの指す認証システムへ取得したtokenでコードを得る
    @param server(string):
    @param token(string)
    @retval bool, code(string) : Falseの場合はbody
    '''

    headers = {"Cookie":"iPlanetDirectoryPro=%s"%token,
               "Content-Type": "application/x-www-form-urlencoded",
               "Cache-Control": "no-cache"}

    jdata = {"response_type":"id_token%20token",
            "scope":"openid",
            "client_id":"sipauthApp",
            "redirect_uri":"https://%s"%server,
            "save_consent":"1",
            "decision":"Allow",
            "nonce":"ZZZZZZ", "state":"ZZZZZZ"}
    #data = urlparse("response_type=code&scope=openid profile qualified email&client_id=sipauthApp&redirect_uri=https://%s&save_consent=1&decision=Allow"%server)
    #data = urlparse("response_type=code&scope=openid&client_id=sipauthApp&redirect_uri=https://%s&save_consent=1&decision=Allow"%server)
    data = urlparse("response_type=id_token token&scope=openid&client_id=sipauthApp&redirect_uri=https://%s&save_consent=1&decision=Allow&nonce=ZZZZZZZ&state=ZZZZZZ"%server)

    #weburl = "https://%s/sso/oauth2/authorize?realm=%s"%(server, realm)
    #weburl = "https://%s/sso/oauth2/%s/authorize?%s"%(server, realm, data.geturl())
    weburl = "https://%s/sso/oauth2/%s/authorize"%(server, realm)

    # simulate this function by curl command for debug
    print("curl command")
    print("curl -X POST \\")
    print('  -H "Cookie:%s" \\'%(headers["Cookie"]))
    print('  -H "Content-Type:%s" \\'%(headers["Content-Type"]))
    print('  -H "Cache-Control: %s" \\'%(headers["Cache-Control"]))
    print("  -d '%s' \\"%data.geturl().replace(" ", "%20"))
    print("  -k -v https://%s/sso/oauth2/%s/authorize"%(server, realm))

    ret, result = openam_post(weburl, json=jdata, headers=headers)
    if ret is False:
        message = result.text.split("\n")
        print("url     = :",weburl)
        print("headers = :",headers)
        print("code =    :",result.status_code)
        print("body =    :"),
        for item in message:
            print("%s"%item)
        return ret, result.text

    #print("code = %s"%urlparse(urllib.unquote(result.url)))
    #items = urllib.unquote(result.url).split('&')
    #print('item no 2 after urlparse and split by &(%s)'%items[2])
    #item = items[2].split("code=")[1]
    #print("code is %s"%item)
    for item in result.__dict__:
        print("key = %s / value = %s"%(item, result.__dict__[item]))
    return ret, item

def openam_getaccess_token(server, code, realm="misystem"):
    '''
    serverの指す認証システムへ取得したcodeでアクセストークンを得る
    @param server(string):
    @param code(string)
    @retval bool, access_token(string) Falseの場合はbody
    '''

    headers = {"Cache-Control": "no-cache"}

    #data = urlparse("client_id=sipauthApp&client_secret=P@ssw0rd&grant_type=authorization_code&realm=%s&code=%s&redirect_uri=https://%s"%(realm, code, server))
    data = urlparse("client_id=sipauthApp&client_secret_basic=P@ssw0rd&grant_type=authorization_code&code=%s&redirect_uri=https://%s"%(code, server))
    jdata = {"client_id":"sipauthApp",
            "client_secret_basic":"P@ssw0rd",
            "grant_type":"authorization_code",
            "realm":"%s"%realm,
            "code":"%s"%code,
            "redirect_uri":"https://%s"%server}

    #weburl = "https://%s/sso/oauth2/%s/access_token&%s"%(server, realm, data.geturl())
    weburl = "https://%s/sso/oauth2/%s/access_token"%(server, realm)
    #weburl = "https://%s/sso/oauth2/access_token?realm=%s"%(server, realm)

    # simulate this function by curl command for debug
    print("curl command")
    print("curl -X POST \\")
    print('  -H "Cache-Control: %s" \\'%(headers["Cache-Control"]))
    print("  -d '%s' \\"%data.geturl().replace(" ", "%20"))
    print("  -k -v https://%s/sso/oauth2/%s/access_token"%(server, realm))

    ret, result = openam_post(weburl, json=jdata, headers=headers)
    #ret, result = openam_post(weburl, json=None, headers=headers)
    if ret is False:
        message = result.text.split("\n")
        print("url     = :",weburl)
        print("headers = :",headers)
        print("code =    :",result.status_code)
        print("body =    :"),
        for item in message:
            print("%s"%item)
        return ret, result.text

    #print("code = %s"%urlparse(urllib.unquote(result.url)))
    #items = urllib.unquote(result.url).split('&')
    #print('item no 2 after urlparse and split by &(%s)'%items[2])
    #item = items[2].split("code=")[1]
    #print("code is %s"%item)
    for item in result.__dict__:
        print("key = %s / value = %s"%(item, result.__dict__[item]))
    return ret, item

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
    if ret is False:
        print("response = ", result)
    else:
        #print("response = %s"%result.text)
        pass

    print("code is %s"%result)
    # access_token取得
    #code = result
    #ret, result = openam_getaccess_token(server, code)

    # userinfo取得

if __name__ == '__main__':

    main()
