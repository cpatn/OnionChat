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
import re

from website.func.database import *
from website.func.session import *

auth = APIRouter()
templates = Jinja2Templates(directory="website/templates")
executor = ThreadPoolExecutor()

USERNAME_REGEX = re.compile(r"^[A-Za-z0-9]{3,21}$")

async def render_template(template_name: str, context: dict):
  return await asyncio.get_event_loop().run_in_executor(
    executor, lambda: templates.get_template(template_name).render(context)
  )

def validate_username(username: str) -> bool:
    return bool(USERNAME_REGEX.fullmatch(username))

@auth.post("/login")
async def post_login(request: Request, username: str = Form(...), password: str = Form(...)):
  error = None
  if not username:
    error = "Invalid Username"
    type = "username"
  if not password:
    error = "Invalid Password"
    type = "password"
  if len(username) < 3 or len(username) > 21:
    error = "Invalid Username Length (min 3 max 21)"
    type = "username"
  if len(password) < 6 or len(password) > 128:
    error = "Invalid Username Length (min 6 max 128)"
    type = "password"
  if not validate_username(username):
    error = "Only Latin Characters and Numbers allowed"
    type = "username"
  user = await loginUser(username, password)
  if user["status"] is not "success":
    if user["status"] == "user_not_found":
      error = "Username not found"
      type = "username"
    elif user["status"] == "wrong_password":
      error = "Wrong password"
      type = "password"
  if error:
    content = await render_template("login/login.html", {"request": request, "error": error, "type": type})
    return HTMLResponse(content=content)
  session = await encrypt(user["user"]["id"], username, user["user"]["displayname"] or username, user["user"]["avatar"], str(datetime.now().isoformat()))
  response = RedirectResponse(url="/@me", status_code=303)
  response.set_cookie(key="session", value=session, httponly=True, samesite="strict")
  return response

@auth.post("/register")
async def post_register(request: Request, username: str = Form(...), password: str = Form(...)):
  error = None
  if not username:
    error = "Invalid Username"
    type = "username"
  if not password:
    error = "Invalid Password"
    type = "password"
  if len(username) < 3 or len(username) > 21:
    error = "Invalid Username Length (min 3 max 21)"
    type = "username"
  if len(password) < 6 or len(password) > 128:
    error = "Invalid Username Length (min 6 max 128)"
    type = "password"
  if not validate_username(username):
    error = "Only Latin Characters and Numbers allowed"
    type = "username"
  user = await addUser(username, password)
  if not user:
    error = "Username taken"
    type = "username"
  if error:
    content = await render_template("login/register.html", {"request": request, "error": error, "type": type})
    return HTMLResponse(content=content)
  session = await encrypt(user, username, username, "default.webp", str(datetime.now().isoformat()))
  response = RedirectResponse(url="/@me", status_code=303)
  response.set_cookie(key="session", value=session, httponly=True, samesite="strict")
  return response