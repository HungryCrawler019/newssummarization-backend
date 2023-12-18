from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
import app.router.api as api_router
import app.router.auth as auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router.router, tags=['api'], prefix="/api")
app.include_router(auth.router, tags=['auth'], prefix="/auth")
