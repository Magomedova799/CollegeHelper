from app.controllers.qr_controller import router as qr_router
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from app.assistant.router import router as assistant_router
from app.db.database import engine
from app.models import Base
from fastapi.responses import FileResponse


from app.controllers import (
    auth_router,
    ticket_router,
    category_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    yield

app = FastAPI(
    title="College Helper API",
    description="Система подачи и обработки заявок колледжа",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(auth_router)

app.include_router(qr_router)

app.include_router(ticket_router)
app.include_router(category_router)

app.include_router(assistant_router)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    return FileResponse(TEMPLATES_DIR / "dashboard.html")

@app.get("/login", include_in_schema=False)
def login_page():
    return FileResponse(TEMPLATES_DIR / "login.html")

