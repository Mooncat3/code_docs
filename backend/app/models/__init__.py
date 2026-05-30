from app.database import Base as BaseDB
from datetime import timezone, datetime

Base = BaseDB


def get_utc_timestamp() -> int:
    return round(datetime.timestamp(datetime.now(timezone.utc)))
