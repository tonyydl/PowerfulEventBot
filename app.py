import os
import sys

import urllib.request
import urllib.parse

from bs4 import BeautifulSoup
from flask import Flask, request, abort
from enum import Enum

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

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

app = Flask(__name__)


class ActionType(Enum):
    MAROON5 = '!maroon5'


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
def handle_message(event):
    main_action = event.message.text.strip()
    print('main_action:{0}\nActionType.MAROON5:{1}'.format(
        main_action, ActionType.MAROON5))
    if main_action == ActionType.MAROON5.value:
        content = action_maroon5()
        print(content)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0


def action_maroon5():
    append_str = ''
    append_str += action_maroon5_khc_concert() + "\n"
    return append_str


def action_maroon5_khc_concert():
    the_title = '「魔力紅2019高雄演唱會」'
    url = 'https://www.livenation.com.tw/show/1214331/maroon-5-red-pill-blues-tour-live-in-kaohsiung-%E9%AD%94%E5%8A%9B%E7%B4%852019%E9%AB%98%E9%9B%84%E6%BC%94%E5%94%B1%E6%9C%83/kaohsiung/2019-03-01/tw'
    response = urllib.request.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    eventtickets = soup.find('div', {'class': 'eventtickets--notickets'})
    if eventtickets is None:
        append_str = '{0}演唱會門票「可能」開始開賣了\n請前往{1}'.format(the_title, url)
        print(append_str)
    else:
        append_str = '{0}演唱會門票目前尚未開賣\n{1}'.format(the_title, url)
        print(eventtickets)
    return append_str


if __name__ == "__main__":
    app.run()
