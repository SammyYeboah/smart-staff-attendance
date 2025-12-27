from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)  # "admin" or "staff"

    attendances: Mapped[list["AttendanceLog"]] = relationship(
        "AttendanceLog", back_populates="user", cascade="all, delete-orphan"
    )

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    __table_args__ = (UniqueConstraint("user_id", "clock_in", name="uq_user_clockin_timestamp"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    clock_in: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    clock_out: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)

    # GPS fields for in/out
    latitude_in: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude_in: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude_out: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude_out: Mapped[float | None] = mapped_column(Float, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="attendances")
