from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.models import Customer
from app.schemas.schemas import CustomerCreate, CustomerResponse, PaginatedResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=PaginatedResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    city: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Lấy danh sách customers với pagination và filter"""
    query = db.query(Customer).filter(Customer.is_active == True)  # noqa: E712

    if city:
        query = query.filter(Customer.city.ilike(f"%{city}%"))
    if search:
        query = query.filter(
            Customer.full_name.ilike(f"%{search}%")
            | Customer.email.ilike(f"%{search}%")
        )

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        items=[CustomerResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=404, detail=f"Không tìm thấy customer: {customer_id}"
        )
    return customer


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Cần quyền admin")

    existing = (
        db.query(Customer)
        .filter(
            (Customer.customer_id == data.customer_id)
            | (Customer.email == data.email)
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409, detail="customer_id hoặc email đã tồn tại"
        )

    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer
