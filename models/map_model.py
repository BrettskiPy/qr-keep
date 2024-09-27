from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TimeBoundParams(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
