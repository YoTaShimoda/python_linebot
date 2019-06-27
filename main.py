# -*- coding: utf-8 -*-


#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.


import os
import sys
from argparse import ArgumentParser
import re
import random


from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)


app = Flask(__name__)


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)


line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)




@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']


    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)


    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)


    return 'OK'




@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    global shimos_position
    global shimos_doing
    shimos_id = 'シモダのユーザidが入ります'
    receive_message = event.message.text
    user_profile = line_bot_api.get_profile(event.source.user_id)
    user_name = user_profile.display_name
    reptoken = event.reply_token
    must_rep = True
    shimoda = ['下田','シモダ','しもだ','陽太','ヨウタ','ようた']

    # 場所用
    position_requests =['どこ','場所']
    # 何してるか用
    doing_request = ['なにしているの？','何しているの','何やっているの','なにやっているの','なにしてるの','何してるの','何してんの','なにしてんの','なにしてる','何してる']
    
    random_rep = ['ランダム返信ワード']

    if user_name == "シモダヨウタ" :
        if receive_message.endswith('now') == True :
            shimos_position = receive_message.replace('now','')
            rep(event.source.user_id,shimos_position)

        elif receive_message.endswith('doing') == True :
            shimos_doing = receive_message.replace('doing','')
            rep(event.source.user_id,shimos_doing)

        else:
            rep(event.source.user_id, random_rep[random.randint(0,len(random_rep))])

    else:
        must_rep = True
        rep(shimos_id,user_name+'から'+receive_message)
        for posi in range(0,len(position_requests)):
            if re.search(position_requests[posi], receive_message) is not None :
                    
                if shimos_position is None :
                    rep(event.source.user_id,'行方不明')
                    must_rep =False
                    break
                    

                else :
                    rep(event.source.user_id,shimos_position+'にいます')
                    must_rep =False
                    break
            
        for doo in range(0,len(doing_request)) :
            if re.search(doing_request[doo],receive_message) is not None :
                if shimos_doing is None :
                    rep(event.source.user_id,'何もしていない')
                    must_rep =False
                    break
                    
                else :
                    rep(event.source.user_id,shimos_doing+'をしています')
                    must_rep =False
                    break

        if must_rep == True :
            rep(event.source.user_id, random_rep[random.randint(0,len(random_rep))])
                    
def rep(token,message):
    line_bot_api.push_message(token, TextSendMessage(text = message))
        
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
