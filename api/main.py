from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os

from .routers import tokens, users, polls, comments

app = FastAPI()

allowed_origins = os.environ.get("CORS_ALLOWED_ORIGINS")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[allowed_origins],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(tokens.router)
app.include_router(users.router)
app.include_router(polls.router)
app.include_router(comments.router)
