import os
from sys import flags, prefix
from linebot.models.messages import ImageMessage, LocationMessage
from linebot.models.send_messages import ImageSendMessage
import requests
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

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
SECRET = os.environ.get('SECRET')

line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)


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


#@handler.add(MessageEvent, message=LocationMessage)
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    res = event.message.text
    #loc = event.message.location
    if res == 'hi' or res == 'Hi':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Hello there'))
    elif res == '-about':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='This chatbot is written by KuoSheng Huang, who is currently struggling in his course homeworks. It would be really kind if you could ignore the, errr..., hollowness? of this work, thank you.'))
    elif res == '-help':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='"Hi" : for greeting, "-about" : for showing the author information, "-help" : for showing all valid commands, you can also send your 位置資訊 to check out where you are.'))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Sorry, I did not expect that message. Please send another valid command or send "-help" for more information.'))


@handler.add(MessageEvent, message=LocationMessage)
def location_msg(event):
    loc = event.message.address
    line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text= 'your current address is ' + loc))

@handler.add(MessageEvent, message=ImageMessage)
def image_msg(event):
    msgId = event.message.id
    message_content = line_bot_api.get_message_content(msgId)#/////raise JSONDecodeError("Expecting value", s, err.value) from None/////, still haven't found out what gone wrong
    with open('./' + str(msgId) + '.png', 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
    url = './' + str(msgId) + '.png'
    msg = {
        "type": "image",
        "originalContentUrl": url,
        "previewImageUrl": url
    }
    line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(original_content_url=url, preview_image_url=url))



if __name__ == "__main__":
    app.run()