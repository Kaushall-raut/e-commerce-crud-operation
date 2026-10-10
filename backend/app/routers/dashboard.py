from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import Customer, Order, OrderDetail, Product
from ..schemas import DashboardSummary, OrderOut, ProductOut, TopProduct

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    zero = Decimal("0.00")
    total_customers = db.scalar(select(func.count()).select_from(Customer)) or 0
    total_products = db.scalar(select(func.count()).select_from(Product)) or 0
    total_orders = db.scalar(select(func.count()).select_from(Order)) or 0
    total_sales = db.scalar(select(func.coalesce(func.sum(Order.total_price - Order.discount), zero))) or zero
    total_discounts = db.scalar(select(func.coalesce(func.sum(Order.discount), zero))) or zero
    threshold = 5
    low_stock_products = db.scalars(
        select(Product).where(Product.product_stock <= threshold).order_by(Product.product_stock, Product.product_name).limit(8)
    ).all()
    recent_orders = db.scalars(
        select(Order).options(joinedload(Order.customer)).order_by(Order.order_datetime.desc(), Order.order_id.desc()).limit(6)
    ).unique().all()
    top_rows = db.execute(
        select(
            Product.product_id,
            Product.product_name,
            func.coalesce(func.sum(OrderDetail.quantity), 0).label("units_sold"),
            func.coalesce(func.sum(OrderDetail.total_price), zero).label("revenue"),
        )
        .join(OrderDetail, OrderDetail.product_id == Product.product_id)
        .group_by(Product.product_id, Product.product_name)
        .order_by(func.sum(OrderDetail.quantity).desc(), Product.product_name)
        .limit(5)
    ).all()
    top_products = [TopProduct(product_id=row.product_id, product_name=row.product_name, units_sold=row.units_sold, revenue=row.revenue) for row in top_rows]
    return DashboardSummary(
        total_customers=total_customers,
        total_products=total_products,
        total_orders=total_orders,
        total_sales=total_sales,
        total_discounts=total_discounts,
        low_stock_products=[ProductOut.model_validate(item) for item in low_stock_products],
        recent_orders=[OrderOut.model_validate(item) for item in recent_orders],
        best_selling_products=top_products,
    )
