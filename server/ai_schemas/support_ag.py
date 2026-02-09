from pydantic import BaseModel, EmailStr
from typing import Literal, Optional

class All_Support(BaseModel):
    auth_token: str
    
