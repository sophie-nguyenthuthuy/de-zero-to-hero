import re
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r"^0\d{9}$")
    city: Optional[str] = None


class CustomerCreate(CustomerBase):
    customer_id: str = Field(..., pattern=r"^C\d{3,}$")

    @field_validator("customer_id")
    @classmethod
    def validate_customer_id(cls, v):
        if not re.match(r"^C\d{3,}$", v):
            raise ValueError("customer_id phải có dạng C001, C002, ...")
        return v


class CustomerResponse(CustomerBase):
    customer_id: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    customer_id: str
    order_date: date = Field(default_factory=date.today)
    total_amount: Decimal = Field(..., gt=0)
    payment_method: Optional[str] = None


class OrderResponse(BaseModel):
    order_id: int
    customer_id: str
    order_date: date
    status: str
    total_amount: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    pages: int


class HealthCheck(BaseModel):
    status: str
    version: str
    db_connected: bool
    timestamp: datetime


# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
