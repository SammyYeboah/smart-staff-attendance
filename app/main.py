from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .database import engine
from .models import Base
from .routes import auth, users, attendance, reports, web

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Staff Attendance API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
)

# API routers
app.include_router(auth.router, prefix="/users", tags=["Auth & Users"])
app.include_router(users.router, prefix="/users", tags=["Auth & Users"])
app.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])

# Web routes and static files
app.include_router(web.router, prefix="/web", tags=["Web"])
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
