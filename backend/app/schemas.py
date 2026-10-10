from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field, field_validator

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class CustomerBase(BaseModel):
    customer_name: str = Field(min_length=1, max_length=100)
    customer_contact: str = Field(min_length=7, max_length=15, pattern=r"^[0-9+() -]+$")
    customer_gender: str | None = Field(default=None, max_length=20)

    @field_validator("customer_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Customer name cannot be blank.")
        return value


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class CustomerOut(CustomerBase):
    model_config = ConfigDict(from_attributes=True)
    customer_id: int


class ProductBase(BaseModel):
    product_image: str | None = Field(default=None, max_length=500)
    product_name: str = Field(min_length=1, max_length=150)
    product_stock: int = Field(ge=0)
    product_price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)

    @field_validator("product_name")
    @classmethod
    def clean_product_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Product name cannot be blank.")
        return value


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    product_id: int


class OrderCreate(BaseModel):
    order_datetime: datetime | None = None
    discount: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)
    customer_id: int = Field(gt=0)


class OrderUpdate(BaseModel):
    order_datetime: datetime | None = None
    discount: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    customer_id: int | None = Field(default=None, gt=0)


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    order_id: int
    order_datetime: datetime
    total_price: Decimal
    discount: Decimal
    customer_id: int
    customer_name: str | None = None
    final_payable: Decimal


class OrderDetailCreate(BaseModel):
    order_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderDetailUpdate(BaseModel):
    order_id: int | None = Field(default=None, gt=0)
    product_id: int | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, gt=0)


class OrderDetailOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    order_detail_id: int
    order_id: int
    product_id: int
    product_name: str | None = None
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class OrderWithDetails(OrderOut):
    details: list[OrderDetailOut] = Field(default_factory=list)


class TopProduct(BaseModel):
    product_id: int
    product_name: str
    units_sold: int
    revenue: Decimal


class DashboardSummary(BaseModel):
    total_customers: int
    total_products: int
    total_orders: int
    total_sales: Decimal
    total_discounts: Decimal
    low_stock_products: list[ProductOut]
    recent_orders: list[OrderOut]
    best_selling_products: list[TopProduct]
