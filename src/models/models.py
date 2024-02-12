from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# class ShortUrl(BaseModel):
#     id: int
#     short_url: str
#     original_url: str
#     active: Optional[bool]
#
#
# class Transition(BaseModel):
#     id: int
#     url_id: int
#     click_date: datetime
#     user_id: Optional[int]
#
#
# class OriginalUrl(BaseModel):
#     original_url: str
