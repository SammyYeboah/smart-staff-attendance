from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserOut, UserList
from ..dependencies import get_current_user, require_admin

router = APIRouter()

@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    return UserOut(id=current_user.id, name=current_user.name, username=current_user.username, role=current_user.role)

@router.get("/list", response_model=UserList)
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.asc()).all()
    return UserList(items=[UserOut(id=u.id, name=u.name, username=u.username, role=u.role) for u in users])
