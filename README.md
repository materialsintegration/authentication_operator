# 概要
MIシステムのシングルサインオンシステムをシェルやpythonから使うためのライブラリ。

## プログラムの配置
適当な場所で、「 git clone ssh://git@gitlab.mintsys.jp:50022/midev/authentication-operator.git 」を実行して、プログラムを取り出し、管理者権限でpipコマンドでインストールします。

```bash
$ su
# cd dist
# pip install openam_operator-x.x.x-py2.py3-none-any.whl
```

## 必要なライブラリ
特にありません。

## 履歴
* 2020/08/08 version 1.0.0 リリース
  + 初版
* 2021/06/01 version 1.1.0 リリース
  + MIntシステム2106（OpenAM14）に対応
* 2021/06/01 version 1.2.0 リリース
  + MIntシステム2004との両方に対応
* 2021/09/21 version 1.3.0 リリース
  + クッキー名「iPlanetDirectoryPro」から「micookie」へ変更対応
  + 2004では動作しないので注意

# プログラムの使用法

## コマンドライン
シェルスクリプトなどでの使用を想定しています。

```
$ python -m openam-operator.openam_operator u-tokyo.mintsys.jp utadmin001 <パスワード>
```
と実行します。
失敗した場合（パスワードが違う、ユーザーIDが違うなど）は以下のようになります。また実行結果として１が返ります。
```
Faild(Unauthorized)
```
成功すれば、
```
ID <500000100000001>
Token <13bedfd69583faa62be240fcbcd0c0c0b542bc92e1352070f150f8a309f441ed>
```
となります。

## ライブラリ
pythonのライブラリとしての実行も想定しています。

* インポート
```python
from openam_operator import openam_operator
```

* 実行  
openam_operator.miauth(server, username, password)   
server : u-tokyo.mintsys.jpのような文字列。  
username : utadmin001のような文字列  
password : パスワード  

* python2.7での実行結果。

```python
>>> opename_operator.miauth("ut-remote.mintsys.jp", "utadmin001", "間違ったパスワード")
(False, <Response [401]>, None)
>>> opename_operator.miauth("ut-remote.mintsys.jp", "utadmin001", "正しいパスワード")
(True, u'500000100000001', u'13bedfd69583faa62be240fcbcd0c0c0b542bc92e1352070f150f8a309f441ed')
```
* python3.xでの実行結果。

```python
>>> opename_operator.miauth("ut-remote.mintsys.jp", "utadmin001", "間違ったパスワード")
(False, <Response [401]>, None)
>>> opename_operator.miauth("ut-remote.mintsys.jp", "utadmin001", "正しいパスワード")
(True, '500000100000001', '13bedfd69583faa62be240fcbcd0c0c0b542bc92e1352070f150f8a309f441ed')
```

## 便利な関数
* ログインプロンプトの表示
  + 実行
    ```
    uid, token = openam_operator.miLogin("dev-u-tokyo.mintsys.jp", "記述子を取得する側(dev-u-tokyo.mintsys.jp)のログイン情報入力")
    ```
  + 表示
    ```
    記述子を取得する側(dev-u-tokyo.mintsys.jp)のログイン情報入力
    ログインID: utadmin01
    パスワード: xxxxx（入力は表示されない）
    ```
  + 戻り値
    - ログインに成功すれば、該当ユーザーのユーザーIDとAPIトークンのタプルが返る。
    - 失敗した場合は、None, Noneとなっているタプルが返る。
