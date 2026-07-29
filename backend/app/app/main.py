from typing import cast
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, users, projects, files, docs
from app.database import engine, Base
from app.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, root_path="/api")

app.add_middleware(
    cast("_MiddlewareClass", CORSMiddleware),
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(files.router)
app.include_router(docs.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Code Documentation API"}
