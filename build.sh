#!/bin/bash
# このライブラリのインストーラ作成にはpython2.7が必要です。
# python2.6またはpython3.xでは動作しません。

# for CentOS7.x
#python setup.py bdist_wheel --universal

# for CentOS6.x with special python install
/usr/local/python2.7/bin/python setup.py bdist_wheel --universal
