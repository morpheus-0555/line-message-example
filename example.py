import sys
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse, PlainTextResponse, JSONResponse
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import Response
from starlette.exceptions import HTTPException
import uvicorn
from linebot import (LineBotApi, WebhookParser)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
)
import logging

templates = Jinja2Templates(directory='templates')

app = Starlette(debug=True)
app.mount('/static', StaticFiles(directory='statics'), name='static')

# get channel_secret and channel_access_token from your environment variable
channel_secret = "get from line developer"
channel_access_token = "get from line developer"

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route('/')
async def homepage(request):
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)


@app.route('/error')
async def error(request):
    """
    An example error. Switch the `debug` setting to see either tracebacks or 500 pages.
    """
    raise RuntimeError("Oh no")


@app.route("/callback", methods=['POST'])
async def callback(request):

    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = await request.body()
    body = body.decode()
    logging.warning(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        HTTPException(400, detail=None)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        logging.warning(event)  #最主要的功能，用以取得 userId 或 groupId。

        # 學舌功能，可確認網站運作正常。
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text=event.message.text))

    return JSONResponse({'success': True})


@app.exception_handler(404)
async def not_found(request, exc):
    """
    Return an HTTP 404 page.
    """
    template = "404.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=404)


@app.exception_handler(500)
async def server_error(request, exc):
    """
    Return an HTTP 500 page.
    """
    template = "500.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)