from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import OrderDetail
from ..schemas import OrderDetailCreate, OrderDetailOut, OrderDetailUpdate, Page
from ..services.order_service import create_order_detail, delete_order_detail, update_order_detail

router = APIRouter(prefix="/order-details", tags=["Order details"])


@router.get("", response_model=Page[OrderDetailOut])
def list_order_details(order_id: int | None = Query(None, gt=0), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    query = select(OrderDetail).options(joinedload(OrderDetail.product))
    count_query = select(func.count()).select_from(OrderDetail)
    if order_id is not None:
        query, count_query = query.where(OrderDetail.order_id == order_id), count_query.where(OrderDetail.order_id == order_id)
    total = db.scalar(count_query) or 0
    items = db.scalars(query.order_by(OrderDetail.order_detail_id.desc()).offset((page - 1) * page_size).limit(page_size)).unique().all()
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=OrderDetailOut, status_code=status.HTTP_201_CREATED)
def add_order_detail(payload: OrderDetailCreate, db: Session = Depends(get_db)):
    item = create_order_detail(db, payload.order_id, payload.product_id, payload.quantity)
    return db.scalar(select(OrderDetail).options(joinedload(OrderDetail.product)).where(OrderDetail.order_detail_id == item.order_detail_id))


@router.get("/{detail_id}", response_model=OrderDetailOut)
def get_order_detail(detail_id: int, db: Session = Depends(get_db)):
    item = db.scalar(select(OrderDetail).options(joinedload(OrderDetail.product)).where(OrderDetail.order_detail_id == detail_id))
    if item is None:
        raise HTTPException(status_code=404, detail=f"Order detail {detail_id} was not found.")
    return item


@router.put("/{detail_id}", response_model=OrderDetailOut)
def edit_order_detail(detail_id: int, payload: OrderDetailUpdate, db: Session = Depends(get_db)):
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    return update_order_detail(db, detail_id, changes)


@router.delete("/{detail_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_order_detail(detail_id: int, db: Session = Depends(get_db)):
    delete_order_detail(db, detail_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
