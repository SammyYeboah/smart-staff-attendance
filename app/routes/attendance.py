from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import AttendanceLog, User
from ..schemas import ClockInRequest, ClockOutRequest, AttendanceOut, AttendanceLogList
from ..dependencies import get_current_user, require_admin
from ..config import settings
from ..utils import within_radius

router = APIRouter()

@router.post("/clock-in", response_model=AttendanceOut)
def clock_in(payload: ClockInRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Enforce location radius
    if not within_radius(
        payload.latitude, payload.longitude,
        settings.INSTITUTION_LAT, settings.INSTITUTION_LON,
        settings.MAX_RADIUS_METERS
    ):
        raise HTTPException(status_code=403, detail="Outside allowed location radius for clock-in")

    entry = AttendanceLog(
        user_id=user.id,
        clock_in=datetime.utcnow(),
        latitude_in=payload.latitude,
        longitude_in=payload.longitude
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return AttendanceOut(
        attendance_id=entry.id, user_id=entry.user_id,
        clock_in=entry.clock_in, clock_out=entry.clock_out,
        latitude_in=entry.latitude_in, longitude_in=entry.longitude_in,
        latitude_out=entry.latitude_out, longitude_out=entry.longitude_out
    )

@router.post("/clock-out", response_model=AttendanceOut)
def clock_out(payload: ClockOutRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = (
        db.query(AttendanceLog)
        .filter(AttendanceLog.user_id == payload.user_id, AttendanceLog.clock_out == None)
        .order_by(AttendanceLog.clock_in.desc())
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="No active clock-in found")

    # Enforce location radius
    if not within_radius(
        payload.latitude, payload.longitude,
        settings.INSTITUTION_LAT, settings.INSTITUTION_LON,
        settings.MAX_RADIUS_METERS
    ):
        raise HTTPException(status_code=403, detail="Outside allowed location radius for clock-out")

    entry.clock_out = datetime.utcnow()
    entry.latitude_out = payload.latitude
    entry.longitude_out = payload.longitude
    db.commit()
    db.refresh(entry)
    return AttendanceOut(
        attendance_id=entry.id, user_id=entry.user_id,
        clock_in=entry.clock_in, clock_out=entry.clock_out,
        latitude_in=entry.latitude_in, longitude_in=entry.longitude_in,
        latitude_out=entry.latitude_out, longitude_out=entry.longitude_out
    )

@router.get("/logs", response_model=AttendanceLogList)
def get_all_logs(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    logs = db.query(AttendanceLog).order_by(AttendanceLog.clock_in.desc()).all()
    items = [
        AttendanceOut(
            attendance_id=l.id, user_id=l.user_id,
            clock_in=l.clock_in, clock_out=l.clock_out,
            latitude_in=l.latitude_in, longitude_in=l.longitude_in,
            latitude_out=l.latitude_out, longitude_out=l.longitude_out
        )
        for l in logs
    ]
    return AttendanceLogList(items=items)

@router.get("/logs/{user_id}", response_model=AttendanceLogList)
def get_user_logs(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not permitted")
    logs = (
        db.query(AttendanceLog)
        .filter(AttendanceLog.user_id == user_id)
        .order_by(AttendanceLog.clock_in.desc())
        .all()
    )
    items = [
        AttendanceOut(
            attendance_id=l.id, user_id=l.user_id,
            clock_in=l.clock_in, clock_out=l.clock_out,
            latitude_in=l.latitude_in, longitude_in=l.longitude_in,
            latitude_out=l.latitude_out, longitude_out=l.longitude_out
        )
        for l in logs
    ]
    return AttendanceLogList(items=items)
