from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/revenue/monthly")
async def monthly_revenue(
    year: int = Query(2024, ge=2020, le=2030),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Doanh thu theo tháng"""
    result = db.execute(
        text(
            """
        SELECT
            EXTRACT(MONTH FROM order_date)::int AS month,
            COUNT(*) AS orders,
            SUM(total_amount)::float AS revenue
        FROM orders
        WHERE status = 'completed'
          AND EXTRACT(YEAR FROM order_date) = :year
        GROUP BY 1
        ORDER BY 1
    """
        ),
        {"year": year},
    )

    return [dict(row._mapping) for row in result]


@router.get("/customers/top")
async def top_customers(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Top customers theo doanh thu"""
    result = db.execute(
        text(
            """
        SELECT c.customer_id, c.full_name, c.city,
               COUNT(o.order_id) AS orders,
               SUM(o.total_amount)::float AS total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.status = 'completed'
        GROUP BY c.customer_id, c.full_name, c.city
        ORDER BY total_spent DESC
        LIMIT :limit
    """
        ),
        {"limit": limit},
    )

    return [dict(row._mapping) for row in result]
