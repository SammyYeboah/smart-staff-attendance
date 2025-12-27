from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import models, database
import bcrypt
from datetime import datetime

templates = Jinja2Templates(directory="app/web/templates")
router = APIRouter()

# ---------------- AUTH ----------------
def authenticate(username: str, password: str, db: Session):
    user = db.query(models.User).filter(models.User.username == username).first()
    if user and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return user
    return None

# ---------------- LOGIN/LOGOUT ----------------
@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_submit(request: Request,
                 username: str = Form(...),
                 password: str = Form(...),
                 db: Session = Depends(database.get_db)):
    user = authenticate(username, password, db)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    # Store session info
    request.session["user_id"] = user.id
    request.session["role"] = user.role
    request.session["name"] = user.name

    if user.role == "staff":
        return RedirectResponse("/web/dashboard", status_code=HTTP_302_FOUND)
    if user.role == "admin":
        return RedirectResponse("/web/admin", status_code=HTTP_302_FOUND)
    if user.role == "db_admin":
        return RedirectResponse("/db-admin", status_code=HTTP_302_FOUND)
    return RedirectResponse("/web/dashboard", status_code=HTTP_302_FOUND)

@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=HTTP_302_FOUND)

# ---------------- STAFF DASHBOARD ----------------
@router.get("/web/dashboard")
def staff_dashboard(request: Request, db: Session = Depends(database.get_db)):
    user_id = request.session.get("user_id")
    name = request.session.get("name")
    if not user_id:
        return RedirectResponse("/login", status_code=HTTP_302_FOUND)

    # Get today's most recent attendance
    today = datetime.utcnow().date()
    latest = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.user_id == user_id
    ).order_by(models.AttendanceLog.clock_in.desc()).first()

    my_today = {"clock_in": None, "clock_out": None, "status": "Absent", "status_class": "absent"}
    if latest and latest.clock_in.date() == today:
        my_today["clock_in"] = latest.clock_in.strftime("%H:%M")
        my_today["clock_out"] = latest.clock_out.strftime("%H:%M") if latest.clock_out else None
        my_today["status"] = "Present" if latest.clock_out else "Working"
        my_today["status_class"] = "present" if latest.clock_out else "working"

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "today_date": today, "my_today": my_today, "name": name}
    )

@router.post("/attendance/clock-in")
def clock_in(request: Request,
             latitude: float | None = Form(None),
             longitude: float | None = Form(None),
             db: Session = Depends(database.get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=HTTP_302_FOUND)

    log = models.AttendanceLog(
        user_id=user_id,
        latitude_in=latitude,
        longitude_in=longitude,
        clock_in=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return RedirectResponse("/web/dashboard", status_code=HTTP_302_FOUND)

@router.post("/attendance/clock-out")
def clock_out(request: Request,
              latitude: float | None = Form(None),
              longitude: float | None = Form(None),
              db: Session = Depends(database.get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=HTTP_302_FOUND)

    log = db.query(models.AttendanceLog).filter(
        models.AttendanceLog.user_id == user_id,
        models.AttendanceLog.clock_out == None
    ).order_by(models.AttendanceLog.clock_in.desc()).first()
    if log:
        log.clock_out = datetime.utcnow()
        log.latitude_out = latitude
        log.longitude_out = longitude
        db.commit()
        db.refresh(log)
    return RedirectResponse("/web/dashboard", status_code=HTTP_302_FOUND)

# ---------------- SCHOOL ADMIN DASHBOARD ----------------
@router.get("/web/admin")
def admin_dashboard(request: Request, db: Session = Depends(database.get_db)):
    role = request.session.get("role")
    if role not in {"admin", "db_admin"}:
        return RedirectResponse("/login", status_code=HTTP_302_FOUND)

    present = db.query(models.AttendanceLog).filter(models.AttendanceLog.clock_in != None).count()
    total_users = db.query(models.User).count()
    absent = max(total_users - present, 0)
    summary = {"present": present, "late": 0, "absent": absent}

    return templates.TemplateResponse("admin.html", {"request": request, "summary": summary})

# ---------------- DB ADMIN PANEL ----------------
@router.get("/db-admin")
def db_admin(request: Request, db: Session = Depends(database.get_db)):
    role = request.session.get("role")
    if role != "db_admin":
        return RedirectResponse("/login", status_code=HTTP_302_FOUND)
    users = db.query(models.User).all()
    return templates.TemplateResponse("db_admin.html", {"request": request, "users": users})

@router.post("/db-admin/users")
def create_user(request: Request,
                name: str = Form(...),
                username: str = Form(...),
                password: str = Form(...),
                role: str = Form(...),
                db: Session = Depends(database.get_db)):

    role_session = request.session.get("role")
    if role_session != "db_admin":
        return RedirectResponse("/login", status_code=HTTP_302_FOUND)

    existing = db.query(models.User).filter(models.User.username == username).first()
    if existing:
        users = db.query(models.User).all()
        return templates.TemplateResponse(
            "db_admin.html",
            {"request": request, "users": users, "error": f"Username '{username}' already exists"}
        )

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_user = models.User(name=name, username=username, password=hashed_pw, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    users = db.query(models.User).all()
    return templates.TemplateResponse(
        "db_admin.html",
        {"request": request, "users": users, "success": "User created successfully"}
    )

@router.get("/db-admin/users/{user_id}/edit")
def edit_user(request: Request, user_id: int, db: Session = Depends(database.get_db)):
    role_session = request.session.get("role")
    if role_session != "db_admin":
        return RedirectResponse("/login", status_code=HTTP_302_FOUND)

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return RedirectResponse("/db-admin", status_code=HTTP_302_FOUND)
    return templates.TemplateResponse("edit_user.html", {"request": request, "user": user})

@router.post("/db-admin/users/{user_id}/update")
def update_user(request: Request,
                user_id: int,
                name: str = Form(...),
                username: str = Form(...),
                role: str = Form(...),
                password: str = Form(""),
                db: Session = Depends(database.get_db)):
    role_session = request.session.get("role")
    if role_session != "db_admin":
        return RedirectResponse("/login", status_code=HTTP_302_FOUND)

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return RedirectResponse("/db-admin", status_code=HTTP_302_FOUND)

    # Prevent duplicate username on update
    existing = db.query(models.User).filter(models.User.username == username, models.User.id != user_id).first()
    if existing:
        users = db.query(models.User).all()
        return templates.TemplateResponse(
            "db_admin.html",
            {"request": request, "users": users, "error": f"Username '{username}' is taken by another user"}
        )

    user.name = name
    user.username = username
    user.role = role

    # Only update password if provided (cannot show original; it’s hashed)
    if password.strip():
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user.password = hashed_pw

    db.commit()
    db.refresh(user)

    users = db.query(models.User).all()
    return templates.TemplateResponse(
        "db_admin.html",
        {"request": request, "users": users, "success": "User updated successfully"}
    )
