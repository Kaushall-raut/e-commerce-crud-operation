from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload
from ..models import Customer, Order, OrderDetail, Product

ZERO = Decimal("0.00")


def _not_found(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


def _lock_order(db: Session, order_id: int) -> Order:
    order = db.scalar(select(Order).where(Order.order_id == order_id).with_for_update())
    if order is None:
        raise _not_found(f"Order {order_id} was not found.")
    return order


def _lock_products(db: Session, product_ids: set[int]) -> dict[int, Product]:
    if not product_ids:
        return {}
    rows = db.scalars(
        select(Product)
        .where(Product.product_id.in_(sorted(product_ids)))
        .order_by(Product.product_id)
        .with_for_update()
    ).all()
    mapping = {product.product_id: product for product in rows}
    missing = product_ids - mapping.keys()
    if missing:
        raise _not_found(f"Product(s) not found: {', '.join(map(str, sorted(missing)))}.")
    return mapping


def _recalculate_order(db: Session, order: Order) -> None:
    subtotal = db.scalar(
        select(func.coalesce(func.sum(OrderDetail.total_price), ZERO)).where(OrderDetail.order_id == order.order_id)
    ) or ZERO
    if order.discount > subtotal:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(f"Discount ({order.discount:.2f}) cannot exceed the order subtotal "
                    f"({subtotal:.2f}). Reduce the discount before removing or changing line items."),
        )
    order.total_price = subtotal


def create_order(db: Session, *, customer_id: int, order_datetime, discount: Decimal) -> Order:
    if db.get(Customer, customer_id) is None:
        raise _not_found(f"Customer {customer_id} was not found.")
    if discount > ZERO:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Create the order with a zero discount first. Add line items, then set the monetary discount.",
        )
    order = Order(customer_id=customer_id, order_datetime=order_datetime, discount=discount, total_price=ZERO)
    db.add(order)
    try:
        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise


def update_order(db: Session, order_id: int, changes: dict) -> Order:
    order = _lock_order(db, order_id)
    if "customer_id" in changes and changes["customer_id"] is not None:
        if db.get(Customer, changes["customer_id"]) is None:
            raise _not_found(f"Customer {changes['customer_id']} was not found.")
    for key, value in changes.items():
        if value is not None:
            setattr(order, key, value)
    subtotal = db.scalar(
        select(func.coalesce(func.sum(OrderDetail.total_price), ZERO)).where(OrderDetail.order_id == order_id)
    ) or ZERO
    if order.discount > subtotal:
        db.rollback()
        raise HTTPException(status_code=409, detail=f"Discount cannot exceed the current subtotal of {subtotal:.2f}.")
    try:
        db.commit()
        return db.scalar(
            select(Order).options(joinedload(Order.customer)).where(Order.order_id == order_id)
        )
    except Exception:
        db.rollback()
        raise


def delete_order(db: Session, order_id: int) -> None:
    order = _lock_order(db, order_id)
    details = db.scalars(
        select(OrderDetail).where(OrderDetail.order_id == order_id).order_by(OrderDetail.order_detail_id).with_for_update()
    ).all()
    products = _lock_products(db, {item.product_id for item in details})
    for item in details:
        products[item.product_id].product_stock += item.quantity
    try:
        db.delete(order)
        db.commit()
    except Exception:
        db.rollback()
        raise


def create_order_detail(db: Session, order_id: int, product_id: int, quantity: int) -> OrderDetail:
    order = _lock_order(db, order_id)
    product = _lock_products(db, {product_id})[product_id]
    if product.product_stock < quantity:
        raise HTTPException(
            status_code=409,
            detail=f"Only {product.product_stock} unit(s) of '{product.product_name}' are available.",
        )
    product.product_stock -= quantity
    unit_price = product.product_price
    line_total = unit_price * quantity
    item = OrderDetail(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price,
        total_price=line_total,
    )
    db.add(item)
    try:
        db.flush()
        _recalculate_order(db, order)
        db.commit()
        db.refresh(item)
        return item
    except Exception:
        db.rollback()
        raise


def update_order_detail(db: Session, detail_id: int, changes: dict) -> OrderDetail:
    # Read once without locking to identify the parent, then take locks in the
    # same order used by order deletion: parent order -> line item -> products.
    observed = db.scalar(select(OrderDetail).where(OrderDetail.order_detail_id == detail_id))
    if observed is None:
        raise _not_found(f"Order detail {detail_id} was not found.")

    observed_order_id = observed.order_id
    new_order_id = changes.get("order_id", observed_order_id)
    order_ids = {observed_order_id, new_order_id}
    orders = db.scalars(
        select(Order).where(Order.order_id.in_(sorted(order_ids))).order_by(Order.order_id).with_for_update()
    ).all()
    order_map = {order.order_id: order for order in orders}
    if len(order_map) != len(order_ids):
        missing = order_ids - order_map.keys()
        raise _not_found(f"Order(s) not found: {', '.join(map(str, sorted(missing)))}.")

    item = db.scalar(select(OrderDetail).where(OrderDetail.order_detail_id == detail_id).with_for_update())
    if item is None:
        raise _not_found(f"Order detail {detail_id} was not found.")
    if item.order_id != observed_order_id:
        db.rollback()
        raise HTTPException(status_code=409, detail="This line item changed while you were editing it. Reload and try again.")

    old_order_id = item.order_id
    old_product_id = item.product_id
    old_quantity = item.quantity
    target_order_id = changes.get("order_id", old_order_id)
    new_product_id = changes.get("product_id", old_product_id)
    new_quantity = changes.get("quantity", old_quantity)

    # If another request changed a field after the initial read, use the row
    # acquired under lock as truth, but reject a target parent we did not lock.
    if target_order_id not in order_map:
        db.rollback()
        raise HTTPException(status_code=409, detail="The target order changed. Reload and try again.")

    products = _lock_products(db, {old_product_id, new_product_id})
    old_product = products[old_product_id]
    new_product = products[new_product_id]

    if new_product_id == old_product_id:
        available = new_product.product_stock + old_quantity
        if new_quantity > available:
            raise HTTPException(status_code=409, detail=f"Only {available} unit(s) of '{new_product.product_name}' are available for this edit.")
        new_product.product_stock = available - new_quantity
        unit_price = item.unit_price
    else:
        old_product.product_stock += old_quantity
        if new_product.product_stock < new_quantity:
            raise HTTPException(status_code=409, detail=f"Only {new_product.product_stock} unit(s) of '{new_product.product_name}' are available.")
        new_product.product_stock -= new_quantity
        unit_price = new_product.product_price

    item.order_id = target_order_id
    item.product_id = new_product_id
    item.quantity = new_quantity
    item.unit_price = unit_price
    item.total_price = unit_price * new_quantity
    try:
        db.flush()
        for order_id in order_ids:
            _recalculate_order(db, order_map[order_id])
        db.commit()
        return db.scalar(
            select(OrderDetail).options(joinedload(OrderDetail.product)).where(OrderDetail.order_detail_id == detail_id)
        )
    except Exception:
        db.rollback()
        raise

def delete_order_detail(db: Session, detail_id: int) -> None:
    observed = db.scalar(select(OrderDetail).where(OrderDetail.order_detail_id == detail_id))
    if observed is None:
        raise _not_found(f"Order detail {detail_id} was not found.")
    observed_order_id = observed.order_id
    order = _lock_order(db, observed_order_id)
    item = db.scalar(select(OrderDetail).where(OrderDetail.order_detail_id == detail_id).with_for_update())
    if item is None:
        raise _not_found(f"Order detail {detail_id} was not found.")
    if item.order_id != observed_order_id:
        db.rollback()
        raise HTTPException(status_code=409, detail="This line item changed while you were editing it. Reload and try again.")
    product = _lock_products(db, {item.product_id})[item.product_id]
    product.product_stock += item.quantity
    try:
        db.delete(item)
        db.flush()
        _recalculate_order(db, order)
        db.commit()
    except Exception:
        db.rollback()
        raise
