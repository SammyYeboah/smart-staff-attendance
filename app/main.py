from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from .views import router
from .database import Base, engine
from .config import settings

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable sessions
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Include routes
app.include_router(router)

# Serve static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
