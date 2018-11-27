## プログラムの配置
適当な場所で、「git clone ssh://git@gitlab.mintsys.jp:50022/midev/authentication-operator.git」を実行して、プログラムを取り出します。

## 必要なライブラリ
特にありません。

# プログラムの使用法

## コマンドライン
シェルスクリプトなどでの使用を想定しています。

```
$ python openam-operator.py u-tokyo.mintsys.jp utadmin001 <パスワード>
```
と実行します。
失敗した場合（パスワードが違う、ユーザーIDが違うなど）は以下のようになります。また実行結果として１が返ります。
```
Faild(Unauthorized)
```
成功すれば、
```
ID <mi-user-id>
Token <mi-api-token>
```
となります。

## ライブラリ
pythonのライブラリとしての実行も想定しています。

* インポート
```python
from openam_operator import *
```

* 実行
miauth(server, username, password)  
server : u-tokyo.mintsys.jpのような文字列。  
username : utadmin001のような文字列  
password : パスワード  

* python2.7での実行結果。

```python
>>> miauth("ut-remote.mintsys.jp", "utadmin001", "間違ったパスワード")
(False, <Response [401]>, None)
>>> miauth("ut-remote.mintsys.jp", "utadmin001", "正しいパスワード")
(True, u'500000100000001', u'13bedfd69583faa62be240fcbcd0c0c0b542bc92e1352070f150f8a309f441ed')
```
* python3.xでの実行結果。

```python
>>> miauth("ut-remote.mintsys.jp", "utadmin001", "間違ったパスワード")
(False, <Response [401]>, None)
>>> miauth("ut-remote.mintsys.jp", "utadmin001", "正しいパスワード")
(True, '500000100000001', '13bedfd69583faa62be240fcbcd0c0c0b542bc92e1352070f150f8a309f441ed')
```

