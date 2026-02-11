from io import BytesIO
import os
import random

from fastapi import Depends, FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.db import SessionLocal, engine
from app.models import Base, SnakeLogin, SnakeGameScore, Upload

app = FastAPI(title="Python Hub")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("ADMIN_SECRET", "change-me"),
    https_only=False,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


def is_admin(request: Request) -> bool:
    return request.session.get("admin") is True


@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_form(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.post("/admin/login", response_class=HTMLResponse)
def admin_login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["admin"] = True
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(
        "admin_login.html",
        {"request": request, "error": "Invalid credentials."},
    )


@app.get("/admin/logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    if not is_admin(request):
        return RedirectResponse("/admin/login", status_code=303)

    recent_uploads = db.query(Upload).order_by(Upload.created_at.desc()).limit(20).all()
    recent_logins = db.query(SnakeLogin).order_by(SnakeLogin.created_at.desc()).limit(20).all()
    recent_scores = (
        db.query(SnakeGameScore)
        .order_by(SnakeGameScore.created_at.desc())
        .limit(20)
        .all()
    )

    return templates.TemplateResponse(
        "admin_dashboard.html",
        {
            "request": request,
            "uploads": recent_uploads,
            "logins": recent_logins,
            "scores": recent_scores,
        },
    )


@app.get("/snake-game", response_class=HTMLResponse)
def snake_game(request: Request):
    return templates.TemplateResponse("snake_game.html", {"request": request})


class SnakeGameResult(BaseModel):
    player_name: str
    score: int
    duration_seconds: int


@app.post("/api/snake-game")
def save_snake_game_result(result: SnakeGameResult, db: Session = Depends(get_db)):
    entry = SnakeGameScore(
        player_name=result.player_name,
        score=result.score,
        duration_seconds=result.duration_seconds,
    )
    db.add(entry)
    db.commit()
    return {"status": "ok"}


@app.get("/snake-login", response_class=HTMLResponse)
def snake_login_form(request: Request):
    return templates.TemplateResponse("snake_login.html", {"request": request})


@app.post("/snake-login", response_class=HTMLResponse)
def snake_login_submit(
    request: Request,
    username: str = Form(...),
    db: Session = Depends(get_db),
):
    login = SnakeLogin(username=username)
    db.add(login)
    db.commit()
    return templates.TemplateResponse(
        "snake_login.html",
        {"request": request, "message": f"Welcome, {username}."},
    )


@app.get("/upload", response_class=HTMLResponse)
def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload", response_class=HTMLResponse)
def upload_submit(
    request: Request,
    python_image: UploadFile | None = File(default=None),
    python_text: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    messages = [
        "That snake is hiss-terical.",
        "Sssstylish upload!",
        "Ssssolid size report.",
        "Sssneak peek approved.",
        "That is one un-snake-able photo.",
        "Ssshowstopper!",
    ]
    message = random.choice(messages)

    if python_image and python_image.filename:
        image_bytes = python_image.file.read()
        image = Image.open(BytesIO(image_bytes))
        width, height = image.size
        upload = Upload(
            kind="image",
            filename=python_image.filename,
            mime_type=python_image.content_type,
            image_bytes=image_bytes,
            width=width,
            height=height,
        )
        db.add(upload)
        db.commit()
        result = {
            "kind": "image",
            "filename": python_image.filename,
            "width": width,
            "height": height,
        }
    elif python_text and python_text.strip():
        clean_text = python_text.strip()
        text_length = len(clean_text)
        upload = Upload(
            kind="text",
            text_content=clean_text,
            text_length=text_length,
        )
        db.add(upload)
        db.commit()
        result = {
            "kind": "text",
            "text_length": text_length,
        }
    else:
        return templates.TemplateResponse(
            "upload.html",
            {"request": request, "error": "Upload an image or type text."},
        )

    return templates.TemplateResponse(
        "result.html",
        {"request": request, "result": result, "message": message},
    )
