from fastapi import FastAPI

from .routers import tokens, users, polls, comments

app = FastAPI()

app.include_router(tokens.router)
app.include_router(users.router)
app.include_router(polls.router)
app.include_router(comments.router)
