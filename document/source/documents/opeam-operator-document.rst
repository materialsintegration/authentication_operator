概要
====

MIシステムのマルチテナントに対応したユーザー認証システムとして、LDAPとOpenAMを使用したSSO(イングルサインオン）を採用した。他方、WF-APIなど各種API使用時には簡易認証方式として登録してあるアクセストークンを使用することになっている。このトークンをAPIゲートウェイのDBに使用するAPIごとに登録し、API使用時登録の有無で使用可能かどうかの認証を行っている。このためAPI使用者は予めこのトークンを入手（ユーザープロファイル画面などから）しておく必要があるが、APIはWEBで実行するだけとは限らず、特にWF-APIではpythonスクリプトなど外部プログラムのみで実行することが多い。このためトークンを入手せず、せっかくあるSSOのシステムを利用し、正式な認証を行いトークンを入手する方法を用意することとした。本書ではこのための手順を記述する。

システム概要
------------

本ライブラリによる認証はOpenAMのREST APIを使用して実施されます。そのためOpenAMにOpenID Connectの設定が必要になります。参考にしたページは以下です。

- `OpenAMのREST-APIメモ（認証、アクセストークン、リフレシュトークン） <https://qiita.com/hakozaki/items/12d1c454c2f9f33a28eb>`__
- `OpenID Providerの実装例～OpenAM～ <https://www.ogis-ri.co.jp/otc/hiroba/technical/openid-connect/chap2.html>`__
- `AWS IAMとOpenAMを連携してアカウント管理を効率化してみた <https://www.ogis-ri.co.jp/otc/hiroba/technical/openid-connect/chap4.html>`__
- `OpenAMから認可コードフローを使ってID連携を試す <https://qiita.com/nanazero/items/56d6bc70b7348dce1aca>`__

実行環境
--------

python（２または３）を想定し、OSはLinux/MacOS/Windowsのどれでも可能とします。またpythonを単独実行しシェルスクリプトなどでも使えるようにします。pythonではライブラリとしての使用を想定しています。

準備
====

手順
----

手順は以下のとおりです。 

- OpenAMにOAuth2プロバイダを作成
- OAuth2.0クライアントとしてエージェントを作成
- 作成したエージェントにいくつかの設定
- デフォルトで取得できるClaim（LDAPの項目）の追加

.. raw:: latex

    \newpage

OpenID Connectの設定
--------------------

1. OpenAMの設定WEBへログインし、misystemレルムを選択します。

.. figure:: ../figures/realm-define.png
   :scale: 70%
   :align: center

   レルムの選択 

.. raw:: latex

    \newpage

2. OAuthプロバイダーの構成を選択します。

.. figure:: ../figures/config-oauthp.png
    :scale: 70%
    :align: center

    構成の選択

.. raw:: latex

    \newpage

3. OpenID Connectの構成を選択します。

.. figure:: ../figures/config-openid.png
    :scale: 70%
    :align: center

    構成の選択

.. raw:: latex

    \newpage

4. 特に何もせず、作成するを押下します。

.. figure:: ../figures/openid-create.png
    :scale: 70%
    :align: center

    作成画面

.. raw:: latex

    \newpage

5. 了解を押下します。

.. figure:: ../figures/openid-confirm.png
    :scale: 70%
    :align: center

    確認画面

.. raw:: latex

    \newpage

6. OAuth2プロバイダができているのを確認します。

.. figure:: ../figures/check-oauth2p.png
    :scale: 70%
    :align: center

    確認画面

.. raw:: latex

    \newpage

OAuth2クライアントの作成
------------------------

1. misystemレルムからAgentsをクリックします。

.. figure:: ../figures/agents.png
    :scale: 70%
    :align: center

    エージェント選択

.. raw:: latex

    \newpage

2. OAuth2クライアントをクリックします。

.. figure:: ../figures/oauth2client.png
    :scale: 70%
    :align: center

    OAuth2クライアント選択

.. raw:: latex

    \newpage

3. 新規にエージェントを作成します。エージェントの新規を押下します。

.. figure:: ../figures/new-agent.png
    :scale: 70%
    :align: center

    新規作成

.. raw:: latex

    \newpage

4. 名前に「sipauthApp」パスワードはPから始まるいつものを設定し、作成を押下します。
5. エージェントにsipauthAppが追加されたのを確認します。

.. figure:: ../figures/confirm-agent.png
    :scale: 70%
    :align: center

    確認画面

.. raw:: latex

    \newpage

エージェントの設定
------------------

1. misystemレルムからAgentをクリックし、OAuth2
   クライアント->sipauthAppをクリック。

-  リダイレクトURIの設定

   -  以下のどれかを設定する。
   -  https://u-tokyo.mintsys.jp(東大運用側)
   -  https://mins.mintsys.jp(NIMS)
   -  https://dev-u-tokyo.mintsys.jp(東大開発側)
   -  https://ut-remote.mintsys.jp(東大リモート環境)

-  スコープの設定

::

    openid
    profile
    qualified
    email

を設定しておく

設定が終わったら右上の保存を押下して、保存する。

-  一旦OpenAMの再起動

::

    # systemctl restart tomcat@openam

-  endopointなどの確認

   WEBブラウザで、https://xxxx.mintsys.jp/sso/oauth2/.well-known/openid-configuration?realm=misystem
   として、以下のようなページ表示が行われれば設定はおおむね大丈夫。

.. raw:: latex

    \newpage

-  chromeの表示

::

    {"response_types_supported":["code token id_token","code","code id_token","id_token","code token","token","token id_token"],"claims_parameter_supported":true,"end_session_endpoint":"http://dev-u-tokyo.mintsys.jp:80/sso/oauth2/misystem/connect/endSession","version":"3.0","check_session_iframe":"http://dev-u-tokyo.mintsys.jp:80/sso/oauth2/misystem/connect/checkSession","scopes_supported":["address","phone","openid","profile","email"],"issuer":"http://dev-u-tokyo.mintsys.jp:80/sso/oauth2/misystem","acr_values_supported":[],"authorization_endpoint":"http://dev-u-tokyo.mintsys.jp:80/sso/oauth2/misystem/authorize","userinfo_endpoint":"http://dev-u-tokyo.mintsys.jp:80/sso/oauth2/misystem/userinfo","claims_supported":["zoneinfo","address","profile","name","phone_number","given_name","locale","family_name","email"],"jwks_uri":"http://dev-u-tokyo.mintsys.jp:80/sso/oauth2/misystem/connect/jwk_uri","subject_types_supported":["public"],"id_token_signing_alg_values_supported":["HS256","HS512","RS256","HS384"],"registration_endpoint":"http://dev-u-tokyo.mintsys.jp:80/sso/oauth2/misystem/connect/register","token_endpoint_auth_methods_supported":["client_secret_post","private_key_jwt","client_secret_basic"],"token_endpoint":"http://dev-u-tokyo.mintsys.jp:80/sso/oauth2/misystem/access_token"}

.. raw:: latex

    \newpage

- Firefoxの表示

.. figure:: ../figures/endpoint-firefox.png
    :scale: 70%
    :align: center

    Firefoxの表示

.. raw:: latex

    \newpage

デフォルトClaimの編集
---------------------
認証成功後最終的にLDAPに登録されている情報を取り出しますが、OpenID Connectが出力できる情報はデフォルトではわずかで、MIシステムで拡張した部分は含まれていません。これを追加しておきます。

1. misystemレルムからScrpitsをクリックします。

.. figure:: ../figures/realm-script.png
    :scale: 70%
    :align: center

    Scriptの選択

.. raw:: latex

    \newpage

2. OIDC Claims Scriptをクリックします。

.. figure:: ../figures/claim-script.png
    :scale: 70%
    :align: center

    Claims Scriptの選択

.. raw:: latex

    \newpage

3. スクリプト編集ウィンドウの中ほどを以下のように編集します。

.. figure:: ../figures/claim-script-window.png
    :scale: 70%
    :align: center

    編集ウィンドウ

.. raw:: latex

    \newpage

claimAttributesに取得方法を追記し、scopeClaimsMapにprofileスコープにmi-user-idとmi-api-tokenを追加します。

::

    claimAttributes = [
            "email": attributeRetriever.curry("mail"),
            "address": { claim, identity, requested -> [ "formatted" : attributeRetriever("postaladdress", claim, identity, requested) ] },
            "phone_number": attributeRetriever.curry("telephonenumber"),
            "given_name": attributeRetriever.curry("givenname"),
            "zoneinfo": attributeRetriever.curry("preferredtimezone"),
            "family_name": attributeRetriever.curry("sn"),
            "locale": attributeRetriever.curry("preferredlocale"),
            "name": attributeRetriever.curry("cn"),
            "mi-user-id": attributeRetriever.curry("mi-user-id"),
            "mi-api-token": attributeRetriever.curry("mi-api-token")  
    ]

    // {scope}: [ {claim}, ... ]
    scopeClaimsMap = [
            "email": [ "email" ],
            "address": [ "address" ],
            "phone": [ "phone_number" ],
            "profile": [ "given_name", "zoneinfo", "family_name", "locale", "name", "mi-user-id", "mi-api-token" ]
    ]

編集が終わったら、右下の「Save」を押下します。

プログラムの使用法
==================

プログラムの配置
----------------

適当な場所で、「git clone ssh://git@gitlab.mintsys.jp:50022/midev/authentication-operator.git」を実行して、プログラムを取り出します。

必要なライブラリ
----------------

特にありません。

コマンドライン
--------------

シェルスクリプトなどでの使用を想定しています。

::

    $ python openam_operator.py u-tokyo.mintsys.jp utadmin001 <パスワード>

と実行します。
失敗した場合（パスワードが違う、ユーザーIDが違うなど）は以下のようになります。また実行結果として１が返ります。

::

    Faild(Unauthorized)

成功すれば、

::

    ID <mi-user-id>
    Token <mi-api-token>

となります。実行結果は0が返ります。

ライブラリ
----------

pythonのライブラリとしての実行も想定しています。

-  インポート

.. code:: python

    from openam_operator import *

-  実行

::

   miauth(server, username, password)
    server   : u-tokyo.mintsys.jpのような文字列。
    username : utadmin001のような文字列
    password : パスワード

- python2.7での実行結果。

.. code:: python

    >>> miauth("ut-remote.mintsys.jp", "utadmin001", "間違ったパスワード")
    (False, <Response [401]>, None)
    >>> miauth("ut-remote.mintsys.jp", "utadmin001", "正しいパスワード")
    (True, u'500000100000001', u'13bedfd69583faa62be240fcbcd0c0c0b542bc92e1352070f150f8a309f441ed')


- python3.xでの実行結果。

.. code:: python
   
    >>> miauth("ut-remote.mintsys.jp", "utadmin001", "間違ったパスワード")
    (False, <Response [401]>, None)
    >>> miauth("ut-remote.mintsys.jp", "utadmin001", "正しいパスワード")
    (True, '500000100000001', '13bedfd69583faa62be240fcbcd0c0c0b542bc92e1352070f150f8a309f441ed')


