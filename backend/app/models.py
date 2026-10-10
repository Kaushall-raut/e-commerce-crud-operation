from datetime import datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_contact: Mapped[str] = mapped_column(String(15), nullable=False)
    customer_gender: Mapped[str | None] = mapped_column(String(20), nullable=True)

    orders: Mapped[list["Order"]] = relationship(back_populates="customer", passive_deletes=True)


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("product_stock >= 0", name="ck_product_stock_nonnegative"),
        CheckConstraint("product_price >= 0", name="ck_product_price_nonnegative"),
    )

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    product_name: Mapped[str] = mapped_column(String(150), nullable=False)
    product_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    product_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order_details: Mapped[list["OrderDetail"]] = relationship(back_populates="product", passive_deletes=True)


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("total_price >= 0", name="ck_order_total_price_nonnegative"),
        CheckConstraint("discount >= 0", name="ck_order_discount_nonnegative"),
    )

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"), server_default="0")
    discount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"), server_default="0")
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id", ondelete="RESTRICT", name="fk_order_customer"), nullable=False)

    customer: Mapped[Customer] = relationship(back_populates="orders")
    details: Mapped[list["OrderDetail"]] = relationship(back_populates="order", cascade="all, delete-orphan", passive_deletes=True)

    @property
    def final_payable(self) -> Decimal:
        return (self.total_price or Decimal("0.00")) - (self.discount or Decimal("0.00"))

    @property
    def customer_name(self) -> str | None:
        return self.customer.customer_name if self.customer else None


class OrderDetail(Base):
    __tablename__ = "order_details"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_detail_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_detail_unit_price_nonnegative"),
        CheckConstraint("total_price >= 0", name="ck_detail_total_price_nonnegative"),
    )

    order_detail_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id", ondelete="CASCADE", name="fk_detail_order"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id", ondelete="RESTRICT", name="fk_detail_product"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    order: Mapped[Order] = relationship(back_populates="details")
    product: Mapped[Product] = relationship(back_populates="order_details")

    @property
    def product_name(self) -> str | None:
        return self.product.product_name if self.product else None
