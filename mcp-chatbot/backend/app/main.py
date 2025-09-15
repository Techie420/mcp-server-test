import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

from .db import DB_BACKEND, init_sql_models
from .auth.jwt import authenticate_user, create_access_token, get_current_user
from .routes.orders import router as orders_router
from .langchain_agent import run_nl_query


app = FastAPI(title="MCP Chatbot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    if DB_BACKEND == "sql":
        init_sql_models(create_all=True)


@app.get("/health")
def health():
    return {"status": "ok", "db_backend": DB_BACKEND}


@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(subject=form_data.username)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/nl-query")
def nl_query(payload: dict, user: str = Depends(get_current_user)):
    text = payload.get("query") or payload.get("text") or ""
    result = run_nl_query(text)
    return result


app.include_router(orders_router)


