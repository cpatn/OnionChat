from fastapi import FastAPI, Request, Response, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from concurrent.futures import ThreadPoolExecutor
import asyncio
from datetime import datetime
from website.routes import create_app

app = create_app()
app.mount("/static", StaticFiles(directory="website/static"), name="static")

templates = Jinja2Templates(directory="website/templates")
executor = ThreadPoolExecutor()

async def render_template(template_name: str, context: dict):
  return await asyncio.get_event_loop().run_in_executor(
    executor, lambda: templates.get_template(template_name).render(context)
  )

if __name__ == "__main__":
    import os
    import sys
    import uvicorn

    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    sys.path.insert(0, os.path.dirname(current_dir))

    uvicorn.run("website.app:app", host="127.0.0.1", port=8080, reload=True)