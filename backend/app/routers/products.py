from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import OrderDetail, Product
from ..schemas import Page, ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=Page[ProductOut])
def list_products(q: str | None = None, stock: str | None = Query(None, pattern="^(available|low|out|all)$"), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    threshold = 5
    query = select(Product)
    count_query = select(func.count()).select_from(Product)
    if q:
        clause = Product.product_name.ilike(f"%{q.strip()}%")
        query, count_query = query.where(clause), count_query.where(clause)
    if stock == "available":
        clause = Product.product_stock > 0
    elif stock == "low":
        clause = Product.product_stock.between(1, threshold)
    elif stock == "out":
        clause = Product.product_stock == 0
    else:
        clause = None
    if clause is not None:
        query, count_query = query.where(clause), count_query.where(clause)
    total = db.scalar(count_query) or 0
    items = db.scalars(query.order_by(Product.product_id.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return Page(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    item = Product(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
        db.refresh(item)
        return item
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Could not create product because of a database constraint.") from exc


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    item = db.get(Product, product_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} was not found.")
    return item


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    item = db.get(Product, product_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} was not found.")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
        db.refresh(item)
        return item
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Could not update product because of a database constraint.") from exc


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    item = db.get(Product, product_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} was not found.")
    is_referenced = db.scalar(select(OrderDetail.order_detail_id).where(OrderDetail.product_id == product_id).limit(1)) is not None
    if is_referenced:
        raise HTTPException(status_code=409, detail="This product is used in order details and cannot be deleted.")
    db.delete(item)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
