from fastapi import APIRouter, HTTPException, Request, Response, Form
from fastapi.requests import HTTPConnection
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote
from datetime import datetime, timedelta
import asyncio
import jinja2
import json

chat = APIRouter()
templates = Jinja2Templates(directory="website/templates")
executor = ThreadPoolExecutor()

async def render_template(template_name: str, context: dict):
  return await asyncio.get_event_loop().run_in_executor(
    executor, lambda: templates.get_template(template_name).render(context)
  )

messages = []

@chat.get("/chat", response_class=HTMLResponse)
async def getchat():
    html = """
    <html>
        <head>
            <meta http-equiv="refresh" content="2">
            <style>
                body { font-family: sans-serif; }
            </style>
        </head>
        <body>
    """

    for m in messages:
        html += f"<p>{m}</p>"

    html += """
        </body>
    </html>
    """

    return html

@chat.post("/send")
async def send(msg: str = Form(...)):
    messages.append(msg)
    return RedirectResponse(url="/chat", status_code=303)