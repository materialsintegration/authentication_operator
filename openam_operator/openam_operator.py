#!/usr/local/python2.7/bin/python
# Copyright (c) The University of Tokyo and
# National Institute for Materials Science (NIMS). All rights reserved.
# This document may not be reproduced or transmitted in any form,
# in whole or in part, without the express written permission of
# the copyright owners.
# -*- coding: utf-8 -*-

'''
OpenAM認証用ライブラリ
'''

import sys, os
import time
import json
import datetime
import requests
import urllib
import subprocess
import base64
import ast
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from getpass import getpass
if sys.version_info[0] <= 2:
    import ConfigParser
    from urlparse import urlparse
    from urllib import unquote as urlunquote
else:
    import configparser
    from urllib.parse import urlparse, quote as urlquote, unquote as urlunquote

# OpenAM認証用クッキーの名前
#OPENAM_COOKIE_NAME="iPlanetDirectoryPro"
OPENAM_COOKIE_NAME="micookie"

def debug_print(result, debugLevel=0):
    '''
    request.SessionのResponseオブジェクトの中身を1次分解して表示する。
    @param result(Responseオブジェクト)
    @retval なし
    '''

    if debugLevel >= 1:
        for item in result.__dict__:
            if item == "raw":
                print("  key = %s / value = %s"%(item, result.__dict__[item].read("_content")))
            elif item == "request":
                print("key = %s / value = %s"%(item, result.__dict__[item]))
                for req_item in result.__dict__[item].__dict__:
                    print("  key = %s / value = %s"%(req_item, result.__dict__[item].__dict__[req_item]))
            else:
                print("key = %s / value = %s"%(item, result.__dict__[item]))

def openam_post(resturl, payload=None, headers=None, debug=0):
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
        debug_print(result, debug)
        return False, result

    return True, result

def openam_get(resturl, payload=None, headers=None, debug=0):
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
        debug_print(result, debug)
        return False, result

    return True, result

def openam_authenticate(server, user_name, user_password, realm="misystem", debug=0):
    '''
    serverの指す認証システムへ認証を実行する
    @param server(string): "https://u-tokyo.mintsys.jp"などのURL
    @param user_name(string)
    @param user_password(string)
    @retval bool, response(dict)
    '''

    if debug >= 1:
        print("------ authenticate to OpenAM ------")
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
        if debug >= 1:
            response = result.json()
            print("Response = {")
            for item in response:
                print("    key = %s / value = %s"%(item, response[item]))
            print("}")

    return ret, result

def openam_getcode(server, token, realm="misystem", debug=0):
    '''
    serverの指す認証システムへ取得したtokenでコードを得る
    @param server(string):
    @param token(string)
    @retval bool, code(string) : Falseの場合はbody
    '''

    if debug >= 1:
        print("------ getting code ------")
    headers = {"Cookie":"%s=%s"%(OPENAM_COOKIE_NAME, token),
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
    #data = urlparse("response_type=code&scope=openid profile qualified email&client_id=sipauthApp&redirect_uri=https://%s&save_consent=1&decision=Allow&nonce=ZZZZZZZ&state=ZZZZZZ"%server)
    data = urlparse("realm=/misystem&response_type=code&scope=openid profile qualified email&client_id=sipauthApp&redirect_uri=https://%s&decision=allow&csrf=%s"%(server, token))

    #weburl = "https://%s/sso/oauth2/authorize?realm=%s"%(server, realm)
    weburl = "https://%s/sso/oauth2/authorize?%s"%(server, data.geturl())
    #weburl = "https://%s/sso/oauth2/%s/authorize"%(server, realm)

    # simulate this function by curl command for debug
    if debug >= 2:
        print("curl command")
        print("curl -X POST \\")
        print('  -H "Cookie:%s" \\'%(headers["Cookie"]))
        print('  -H "Content-Type:%s" \\'%(headers["Content-Type"]))
        print('  -H "Cache-Control: %s" \\'%(headers["Cache-Control"]))
        print("  -d '%s' \\"%data.geturl().replace(" ", "%20"))
        print("  -k -v https://%s/sso/oauth2/authorize"%(server))

    #ret, result = openam_post(weburl, json=jdata, headers=headers)
    ret, result = openam_post(weburl, payload=None, headers=headers)
    if ret is False:
        debug_print(result, debug)
        return ret, result.text

    items = urlunquote(result.url).split('&')
    code = None
    if debug >= 1:
        print("url = %s"%result.url)
        #for item in vars(result):
        #    print("%s = %s"%(item, vars(result)[item]))
        for item in items:
            print(item)
    #items = urllib.unquote(result.url).split('&')
    for item in items:
        if item.startswith("code") is True:
            code = item.split("=")[1]
        if item.startswith("goto") is True:
            subitem = item.split("?")[1]
            if subitem.startswith("code") is True:
                code = subitem.split("=")[1]
    #item = items[2].split("code=")[1]
    if debug >= 1:
        print("code is %s"%code)

    return True, code

def openam_getaccess_token(server, code, realm="misystem", debug=0):
    '''
    serverの指す認証システムへ取得したcodeでアクセストークンを得る
    @param server(string):
    @param code(string)
    @retval bool, access_token(string) Falseの場合はbody
    '''

    if debug >= 1:
        print("------ getting access_token ------")
    headers = {"Cache-Control": "no-cache",
               "Content-Type": "application/x-www-form-urlencoded",
               #"Authorization": "Basic %s"%base64.b64encode(b"sipauthApp:P@ssw0rd")}
               #"Authorization": "Basic %s"%base64.encodestring("sipauthApp:P@ssw0rd".encode("utf-8")).decode("ascii")}
               "Authorization": "Basic c2lwYXV0aEFwcDpQQHNzdzByZA=="}

    jdata = {'grant_type':'authorization_code',
             'code':'%s'%code,
             'redirect_uri':'https://%s'%server}

    data = urlparse("realm=/misystem&grant_type=authorization_code&code=%s&redirect_uri=https://%s"%(code, server))

    #weburl = "https://%s/sso/oauth2/%s/access_token"%(server, realm)
    #weburl = "https://%s/sso/oauth2/%s/access_token?%s"%(server, realm, data.geturl())
    weburl = "https://%s/sso/oauth2/access_token?%s"%(server, data.geturl())

    # simulate this function by curl command for debug
    if debug >= 2:
        print("curl command")
        print("curl -X POST \\")
        print('  -H "Cache-Control: %s" \\'%headers["Cache-Control"])
        print('  -H "Authorization: %s" \\'%headers["Authorization"])
        print("  -d '%s' \\"%data.geturl().replace(" ", "%20"))
        print("  -k -v https://%s/sso/oauth2/%s/access_token"%(server, realm))

    #ret, result = openam_post(weburl, headers=headers, payload=jdata)
    ret, result = openam_post(weburl, payload=None, headers=headers)
    if ret is False:
        debug_print(result, debug)
        return ret, result
    else:
        response = result.json()
        if debug >= 1:
            print("Response = {")
            for item in response:
                print("    key = %s / value = %s"%(item, response[item]))
            print("}")
    
        return ret, result.json()["access_token"]

def openam_get_userinfo(server, access_token, realm="misystem", debug=0):
    '''
    serverの指す認証システムへ取得したaccess_tokenでユーザー情報を得る
    @param server(string):
    @param access_token(string)
    @param realm(string)
    @retval bool, access_token(string) Falseの場合はbody
    '''

    if debug >= 1:
        print("------ getting user informations ------")
    headers = {"Authorization":"Bearer %s"%access_token}

    #weburl = "https://%s/sso/oauth2/%s/userinfo"%(server, realm)
    weburl = "https://%s/sso/oauth2/userinfo?realm=%s"%(server, realm)
    #weburl = "https://%s/sso/oauth2/userinfo"%(server)

    # simulate this function by curl command for debug
    if debug >= 2:
        print("curl command")
        print("curl -X POST \\")
        print('  -H "Authorization: %s" \\'%(headers["Authorization"]))
        print("  -d 'claims=mi-api-token&scope=mi-api-token' \\")
        print("  -k -v https://%s/sso/oauth2/userinfo?realm=%s"%(server, realm))

    ret, result = openam_get(weburl, payload={"claims":"mi-api-token"}, headers=headers)
    if ret is False:
        return ret, result
    else:
        if debug >= 1:
            print("Response = {")
            for item in result.json():
                print("    key = %s / value = %s"%(item, result.json()[item]))

            print("}")
        return ret, result.json()

def openam_getinfo(server, token, realm="misystem", debug=0):
    '''
    serverの指す認証システムへ取得したtokenで得られる情報を得る。（GET Method使用）
    20210519:Y.Manaka openam_getcodeがOpenAM14のOAuth2でうまく動かなかったので、こちらで代用で作り始めたが
                      うまく動くようになったので、開発は途中まで。
                    　動作は、GETで取得したHTMLからmi-user-idとmi-api-tokenを抜き出す。
    @param server(string):
    @param token(string)
    @retval bool, code(string) : Falseの場合はbody
    '''

    if debug >= 1:
        print("------ getting code ------")
    headers = {"Cookie":"%s=%s"%(OPENAM_COOKIE_NAME, token),
               "Content-Type": "application/x-www-form-urlencoded",
    #headers = {"Authorization":"Basic %s"%token,
    #           "Content-Type": "application/json",
               "Cache-Control": "no-cache"}

    jdata = {"response_type":"id_token",
            "scope":"openid profile mi-user-id Mi-User-Id qualified email",
            "client_id":"sipauthApp",
            "redirect_uri":"https://%s"%server,
            "save_consent":"1",
            "decision":"Allow"}
    #        "nonce":"ZZZZZZ", "state":"ZZZZZZ"}

    #data = urlparse("response_type=id_token token&scope=openid&client_id=sipauthApp&redirect_uri=https://%s&save_consent=1&decision=Allow&nonce=ZZZZZZZ&state=ZZZZZZ"%server)
    #data = urlparse("response_type=code&scope=openid profile qualified email&client_id=sipauthApp&redirect_uri=https://%s&save_consent=1&decision=Allow&nonce=ZZZZZZZ&state=ZZZZZZ"%server)
    data = urlparse("realm=/%s&response_type=code&scope=openid profile qualified email&client_id=sipauthApp&redirect_uri=https://%s&save_consent=1&decision=Allow&nonce=ZZZZZZZ&state=ZZZZZZ"%(realm, server))

    weburl = "https://%s/sso/oauth2/authorize?%s"%(server, data.geturl())
    #weburl = "https://%s/sso/oauth2/%s/authorize?%s"%(server, realm, data.geturl())

    # simulate this function by curl command for debug
    if debug >= 2:
        print("curl command")
        #print("curl -X POST \\")
        print("curl -X GET \\")
        print('  -H "Cookie:%s" \\'%(headers["Cookie"]))
        #print('  -H "Authorization:%s" \\'%(headers["Authorization"]))
        print('  -H "Content-Type:%s" \\'%(headers["Content-Type"]))
        print('  -H "Cache-Control: %s" \\'%(headers["Cache-Control"]))
        print("  -d '%s' \\"%data.geturl().replace(" ", "%20"))
        #print("  -k -v https://%s/sso/oauth2/%s/authorize"%(server, realm))
        print("  -k -v https://%s/sso/oauth2/authorize"%server)

    #ret, result = openam_post(weburl, json=jdata, headers=headers)
    #ret, result = openam_post(weburl, payload=None, headers=headers)
    ret, result = openam_get(weburl, payload=None, headers=headers)
    if ret is False:
        debug_print(result, debug)
        return ret, result.text

    if debug >= 1:
        for item in vars(result):
            print("%s = %s"%(item, vars(result)[item]))
    content = result.content.decode("utf-8").replace("\n", "").strip()
    print(content)
    parser = HTMLParser()
    parser.feed(content)
    print(parser.handle_data("script"))
    #items = urllib.unquote(result.url).split('&')
    #items = urlunquote(result.url).split('&')
    #if debug >= 1:
    #    for item in items:
    #        print(item)
    #item = items[2].split("code=")[1]
    if debug >= 1:
        print("code is %s"%item)

    return True, item

def miauth(server, user_name, user_passwd, debug=0):
    '''
    MIシステムの認証。認証が通ればmi-user-idとmi-api-tokenが返る
    @param user_name(string)
    @param user_passwd(string)
    @param debug(int)
    @retval bool, string, string(認証失敗なら、False, None, Noneとなる)
    '''

    # 初期認証
    ret, result = openam_authenticate(server, user_name, user_passwd, debug=debug)
    if ret is False:
        #print("response = ", result)
        return False, result, None

    if debug >= 1:
        print("認証OK")
    # code取得
    token = result.json()["tokenId"]
    ret, result = openam_getcode(server, token, debug=debug)
    if ret is False:
        return False, result, None

    # access_token取得
    code = result
    ret, result = openam_getaccess_token(server, code, debug=debug)
    if ret is False:
        return False, result, None

    access_token = result
    if debug >= 2:
        print("access_token is %s"%access_token)

    # userinfo取得
    ret, result = openam_get_userinfo(server, access_token, debug=debug)

    if ret is True:
        return True, result["mi-user-id"], result["mi-api-token"]
    else:
        return False, result, None

def miLogin(hostname, message=None):
    '''
    ログイン
    @param hostname (string) dev-u-tokyo.mintsys.jpなどのサイト名
    @param message (string) ログインの前に表示するメッセージ。無い場合は"<hostname>へのログイン"が表示される。
    @retval userid, tokenのタプルが返る。ログインに失敗した場合None, Noneのタプルが返る。
    '''

    #print("記述子を登録する側のログイン情報入力")
    if message is None:
        print("%s へのログイン"%hostname)
    else:
        print(message)
    if sys.version_info[0] <= 2:
        name = raw_input("ログインID: ")
    else:
        name = input("ログインID: ")
    password = getpass("パスワード: ")

    ret, uid, token = miauth(hostname, name, password)
    if ret is False:
        if uid.status_code == 401:
            print(uid.json()["message"])
        return None, None

    return uid, token

def main():
    '''
    コマンドラインからの実行開始点
    '''

    params_len = len(sys.argv)
    if params_len < 4:
        print("usage :")
        print("python authentication-operater.py <server> <user name> <password>")
        print(" ")
        print("      server: u-tokyo.mintsys.jpのようなURL")
        print("    username: utadmin01のようなID")
        print("    password: パスワード")
        sys.exit(1)

    server = sys.argv[1]
    user_name = sys.argv[2]
    user_passwd = sys.argv[3]
    debug_level = 0
    if len(sys.argv) == 5:
        try:
            debug_level = int(sys.argv[4])
            print("set debug_level %d"%debug_level)
        except:
            pass

    # 認証
    ret, uid, token = miauth(server, user_name, user_passwd, debug_level)

    if ret is True:
        print("ID %s"%uid)
        print("Token %s"%token)
    else:
        if isinstance(uid, requests.models.Response) is True:
            debug_print(uid, debug_level)
            print("Faild(%s)"%uid.reason)
        else:
            print("reason = %s"%uid)
        sys.exit(1)

if __name__ == '__main__':

    main()
