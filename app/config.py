import os
from pydantic import BaseModel

class Settings(BaseModel):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:guggisburg@localhost:5432/smart_staff_attendance_db",
    )

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_this_in_env_to_a_long_random_string")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

    # Location rules (institution coordinates + max radius in meters)
    # NOTE: Your provided coordinates are used as-is. If -0196003 is a typo, update INSTITUTION_LON accordingly.
    INSTITUTION_LAT: float = float(os.getenv("INSTITUTION_LAT", "5.669533"))
    INSTITUTION_LON: float = float(os.getenv("INSTITUTION_LON", "-0196003"))
    MAX_RADIUS_METERS: int = int(os.getenv("MAX_RADIUS_METERS", "50"))

settings = Settings()
