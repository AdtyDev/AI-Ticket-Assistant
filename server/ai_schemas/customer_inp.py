from pydantic import BaseModel, EmailStr
from typing import Optional, Literal


class ShowCustomers(BaseModel):
    auth_token: str | None


