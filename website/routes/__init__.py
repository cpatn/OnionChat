from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

def create_app():
  app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
  app.mount("/static", StaticFiles(directory="website/static"), name="static")

  from .main import main
  app.include_router(main)
  from .chat import chat
  app.include_router(chat)
  from .auth import auth
  app.include_router(auth)

  return app