from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload
from ..database import get_db
from ..models import Order, OrderDetail
from ..schemas import OrderCreate, OrderOut, OrderUpdate, OrderWithDetails, Page
from ..services.order_service import create_order, delete_order, update_order

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=Page[OrderOut])
def list_orders(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(Order)) or 0
    items = db.scalars(
        select(Order).options(joinedload(Order.customer))
        .order_by(Order.order_datetime.desc(), Order.order_id.desc())
        .offset((page - 1) * page_size).limit(page_size)
    ).unique().all()
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def add_order(payload: OrderCreate, db: Session = Depends(get_db)):
    order = create_order(db, customer_id=payload.customer_id, order_datetime=payload.order_datetime, discount=payload.discount)
    return db.scalar(select(Order).options(joinedload(Order.customer)).where(Order.order_id == order.order_id))


@router.get("/{order_id}", response_model=OrderWithDetails)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.scalar(
        select(Order).options(joinedload(Order.customer), selectinload(Order.details).joinedload(OrderDetail.product))
        .where(Order.order_id == order_id)
    )
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} was not found.")
    return order


@router.put("/{order_id}", response_model=OrderOut)
def edit_order(order_id: int, payload: OrderUpdate, db: Session = Depends(get_db)):
    changes = payload.model_dump(exclude_unset=True)
  
    return update_order(db, order_id, changes)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_order(order_id: int, db: Session = Depends(get_db)):
    delete_order(db, order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
