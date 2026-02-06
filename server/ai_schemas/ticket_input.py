from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional


class CreateTicketInput(BaseModel):
    customer_email: Optional[EmailStr]
    title: str
    description: str
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    auth_token: str   # injected at runtime



