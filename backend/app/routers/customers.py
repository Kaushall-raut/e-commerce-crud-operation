
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Customer, Order
from ..schemas import CustomerCreate, CustomerOut, CustomerUpdate, Page


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["Customers"])


#  List customers with search and pagination
@router.get("", response_model=Page[CustomerOut])
def list_customers(
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        query = select(Customer)
        count_query = select(func.count()).select_from(Customer)

        if q and q.strip():
            search_term = f"%{q.strip()}%"
            query = query.where(
                Customer.customer_name.ilike(search_term)
            )
            count_query = count_query.where(
                Customer.customer_name.ilike(search_term)
            )

        total = db.scalar(count_query) or 0

        items = db.scalars(
            query.order_by(Customer.customer_id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()

        return Page(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    except SQLAlchemyError as exc:
        logger.exception("Database error while listing customers")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving customers. Check the backend terminal.",
        ) from exc


#  Create a customer
@router.post(
    "",
    response_model=CustomerOut,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
):
    try:
        item = Customer(**payload.model_dump())

        db.add(item)
        db.commit()
        db.refresh(item)

        return item

    except IntegrityError as exc:
        db.rollback()
        logger.exception("Integrity error while creating customer")

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create customer because of a database constraint.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Database error while creating customer")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error. Check the backend terminal.",
        ) from exc


#Retrieve one customer
@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    try:
        item = db.get(Customer, customer_id)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {customer_id} was not found.",
            )

        return item

    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception(
            "Database error while retrieving customer %s",
            customer_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving customer.",
        ) from exc


# Update a customer
@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
):
    try:
        item = db.get(Customer, customer_id)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {customer_id} was not found.",
            )

        update_data = payload.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(item, key, value)

        db.commit()
        db.refresh(item)

        return item

    except HTTPException:
        raise

    except IntegrityError as exc:
        db.rollback()
        logger.exception(
            "Integrity error while updating customer %s",
            customer_id,
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update customer because of a database constraint.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception(
            "Database error while updating customer %s",
            customer_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating customer.",
        ) from exc


# Delete a customer if they have no orders
@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    try:
        item = db.get(Customer, customer_id)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {customer_id} was not found.",
            )

        has_orders = db.scalar(
            select(Order.order_id)
            .where(Order.customer_id == customer_id)
            .limit(1)
        ) is not None

        if has_orders:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This customer has orders and cannot be deleted. "
                    "Delete or reassign the orders first."
                ),
            )

        db.delete(item)
        db.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException:
        raise

    except IntegrityError as exc:
        db.rollback()
        logger.exception(
            "Integrity error while deleting customer %s",
            customer_id,
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer cannot be deleted because related records exist.",
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception(
            "Database error while deleting customer %s",
            customer_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while deleting customer.",
        ) from exc
