from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers.meetings import router

app = FastAPI()
app.include_router(router)
app.mount("/",StaticFiles(directory="app/static", html=True), name="static")