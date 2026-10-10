import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .routers import customers, products, orders, order_details, dashboard

load_dotenv()
app = FastAPI(
    title="E-commerce Management API",
    description="CRUD APIs for customers, products, orders, order details, and dashboard statistics.",
    version="1.0.0",
)
origins = [value.strip() for value in os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",") if value.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(customers.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(order_details.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "ecommerce-management-api"}


@app.exception_handler(IntegrityError)
async def handle_integrity_error(_: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "The request conflicts with existing database data or a database constraint."})


@app.exception_handler(SQLAlchemyError)
async def handle_database_error(_: Request, exc: SQLAlchemyError):
    return JSONResponse(status_code=500, content={"detail": "A database error occurred. Verify the PostgreSQL connection and schema."})


@app.exception_handler(RequestValidationError)
async def handle_validation_error(_: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content=jsonable_encoder({"detail": exc.errors()}))
