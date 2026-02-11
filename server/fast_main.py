from fastapi import FastAPI
from server.assistant import router as assistant_router
from server.routes.history import router as history_router
from server.routes.session import router as __router

app = FastAPI()

app.include_router(assistant_router)

app.include_router(history_router)

app.include_router(__router)