from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import AttendanceLog, User
from ..schemas import DailySummaryFilter, UserLogsFilter, AttendanceLogList, AttendanceOut
from ..dependencies import require_admin

router = APIRouter()

@router.post("/daily-summary", response_model=AttendanceLogList)
def daily_summary(filter: DailySummaryFilter, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    target = datetime.strptime(filter.date, "%Y-%m-%d").date()
    start_dt = datetime.combine(target, datetime.min.time())
    end_dt = datetime.combine(target, datetime.max.time())
    logs = (
        db.query(AttendanceLog)
        .filter(AttendanceLog.clock_in >= start_dt, AttendanceLog.clock_in <= end_dt)
        .order_by(AttendanceLog.clock_in.asc())
        .all()
    )
    items = [AttendanceOut(attendance_id=l.id, user_id=l.user_id, clock_in=l.clock_in, clock_out=l.clock_out) for l in logs]
    return AttendanceLogList(items=items)

@router.post("/user-range", response_model=AttendanceLogList)
def user_range(filter: UserLogsFilter, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    query = db.query(AttendanceLog).filter(AttendanceLog.user_id == filter.user_id)
    if filter.start_date:
        start_dt = datetime.strptime(filter.start_date, "%Y-%m-%d")
        query = query.filter(AttendanceLog.clock_in >= start_dt)
    if filter.end_date:
        end_dt = datetime.strptime(filter.end_date, "%Y-%m-%d")
        query = query.filter(AttendanceLog.clock_in <= end_dt)
    logs = query.order_by(AttendanceLog.clock_in.asc()).all()
    items = [AttendanceOut(attendance_id=l.id, user_id=l.user_id, clock_in=l.clock_in, clock_out=l.clock_out) for l in logs]
    return AttendanceLogList(items=items)

@router.post("/export-csv")
def export_csv(filter: DailySummaryFilter, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    target = datetime.strptime(filter.date, "%Y-%m-%d").date()
    start_dt = datetime.combine(target, datetime.min.time())
    end_dt = datetime.combine(target, datetime.max.time())
    logs = (
        db.query(AttendanceLog)
        .filter(AttendanceLog.clock_in >= start_dt, AttendanceLog.clock_in <= end_dt)
        .order_by(AttendanceLog.clock_in.asc())
        .all()
    )
    lines = ["attendance_id,user_id,clock_in,clock_out"]
    for l in logs:
        clock_in = l.clock_in.isoformat()
        clock_out = l.clock_out.isoformat() if l.clock_out else ""
        lines.append(f"{l.id},{l.user_id},{clock_in},{clock_out}")
    csv_data = "\n".join(lines)
    return Response(content=csv_data, media_type="text/csv")
