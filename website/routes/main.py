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

from website.func.session import encrypt, decrypt

main = APIRouter()
templates = Jinja2Templates(directory="website/templates")
executor = ThreadPoolExecutor()

async def render_template(template_name: str, context: dict):
  return await asyncio.get_event_loop().run_in_executor(
    executor, lambda: templates.get_template(template_name).render(context)
  )

@main.get("/")
async def read_root(request: Request):
    content = await render_template('index.html', {"request": request})
    return HTMLResponse(content=content)

@main.get("/login")
async def login(request: Request):
   session = request.cookies.get("session")
   if session:
      user = await decrypt(session)
      if user:
         return RedirectResponse("/@me")
   content = await render_template("login/login.html", {"request": request})
   return HTMLResponse(content)

@main.get("/register")
async def register(request: Request):
   session = request.cookies.get("session")
   if session:
      user = await decrypt(session)
      if user:
         return RedirectResponse("/@me")
   content = await render_template("login/register.html", {"request": request})
   return HTMLResponse(content)