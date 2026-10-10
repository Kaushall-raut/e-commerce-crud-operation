# CommerceDesk — E-commerce CRUD

A full-stack e-commerce **management** app built with Angular 21, Tailwind CSS 4, FastAPI, SQLAlchemy 2, Pydantic 2, and PostgreSQL. It includes CRUD operations for customers, products, orders, and order details, plus a live dashboard. There is **no login, registration, authentication, or authorization**.

## Project structure

```text
ecommerce-crud/
├── backend/
│   ├── app/
│   │   ├── main.py, database.py, models.py, schemas.py, init_db.py
│   │   ├── routers/{customers,products,orders,order_details,dashboard}.py
│   │   └── services/order_service.py
│   ├── requirements.txt
│   └── .env.example
├── database/{schema.sql,seed.sql}
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── app.component.ts, app.config.ts, app.routes.ts
    │   │   ├── core/{models,services}/
    │   │   └── pages/{dashboard,customers,products,orders,order-details}/
    │   ├── environments/environment.ts
    │   ├── main.ts
    │   └── styles.css
    ├── .postcssrc.json
    ├── angular.json
    ├── package.json
    └── tsconfig.json
```

## 1. Configure PostgreSQL on Windows

1. Install PostgreSQL and open **pgAdmin** (or SQL Shell/`psql`).
2. Create a database named `ecommerce_db`. In pgAdmin's Query Tool connected to your PostgreSQL server, run:

   ```sql
   CREATE DATABASE ecommerce_db;
   ```

   If it already exists, do not recreate it.

3. Connect to `ecommerce_db`. Open `database/schema.sql` in pgAdmin's Query Tool and execute it. The DDL creates missing tables without dropping existing ones. For an existing database, inspect its current columns and constraints first; `CREATE TABLE IF NOT EXISTS` does not repair a table whose existing definition differs. Apply a reviewed `ALTER TABLE` migration for any needed differences.
4. Optional: execute `database/seed.sql` to insert two sample customers and three sample products. The seed is safe to rerun for the same sample names/contacts.
5. Make a copy of `backend/.env.example` named `backend/.env`, then set `DATABASE_URL` to the username/password configured on your computer. Example:

   ```env
   DATABASE_URL=postgresql+psycopg://postgres:YourPostgresPassword@localhost:5432/ecommerce_db
   CORS_ORIGINS=http://localhost:4200
   ```

   URL-encode any special characters in the password (for example, `@` becomes `%40`). Do not commit the `.env` file.

## 2. Start FastAPI

Open PowerShell in the project folder:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and set your PostgreSQL credentials before the next command.
python -m app.init_db
uvicorn app.main:app --reload
```

`python -m app.init_db` uses SQLAlchemy `create_all`: it creates missing tables, but deliberately does **not** alter existing tables. It is suitable for an empty/new database. For a pre-existing database, inspect it first and apply reviewed migrations as required. `database/schema.sql` is the canonical schema.

Check:

- API docs: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>
- Dashboard summary JSON: <http://127.0.0.1:8000/api/dashboard/summary>

Keep this PowerShell window open while using the frontend.

## 3. Start Angular 21 + Tailwind CSS

Use a supported Node.js version: `20.19+`, `22.12+`, or `24.x` is compatible with Angular 21. Node 22 LTS is a good default.

Open a **second** PowerShell window:

```powershell
cd frontend
npm install
npx ng serve
```

Open <http://localhost:4200>. The frontend calls `http://127.0.0.1:8000/api`; if the API host/port changes, update `frontend/src/environments/environment.ts` and update `CORS_ORIGINS` in `backend/.env`.

## Business rules implemented

- Monetary values use PostgreSQL `NUMERIC` and Python `Decimal` in the backend.
- `order_details.total_price = unit_price × quantity`.
- `orders.total_price` is the sum of its line items before discount. `orders.discount` is a fixed monetary amount and the API rejects discounts greater than the subtotal. Payable is `total_price - discount`.
- A new order starts with a zero discount because it has no line items yet. Add line items first; then edit the order to apply a discount.
- On line-item creation, the current catalog price is snapshotted as `unit_price`. Changing only quantity preserves that saved unit price. Changing the product refreshes the line's unit price from that product's current catalog price.
- Adding line items deducts stock; changing quantities/products adjusts stock; removing a line item restores stock. Deleting an order restores its item quantities before deleting the order and its details.
- Product rows are locked with `SELECT ... FOR UPDATE` before checking/updating stock to reduce concurrent overselling. The related stock, line-item, and order-total changes commit or roll back together.
- Customers with orders and products referenced by order details cannot be deleted (HTTP 409). The schema deliberately has no order-status, email, location, or authentication fields.
- The dashboard reports total counts, net sales after discounts, total discounts, low-stock products (threshold is 5 units), recent orders, and best-selling products.

## API endpoint reference

All collection endpoints are paginated and return `{ "items": [], "total": 0, "page": 1, "page_size": 20 }`. The default page size is 20; `page_size` is limited to 100.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/customers?q=aarav&page=1&page_size=20` | List/search customers |
| POST | `/api/customers` | Create customer |
| GET | `/api/customers/{id}` | Get customer |
| PUT | `/api/customers/{id}` | Update customer |
| DELETE | `/api/customers/{id}` | Delete customer (409 if orders exist) |
| GET | `/api/products?q=watch&stock=available` | List/search/filter products (`all`, `available`, `low`, `out`) |
| POST | `/api/products` | Create product |
| GET | `/api/products/{id}` | Get product |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product (409 if referenced by an order detail) |
| GET | `/api/orders?page=1&page_size=20` | List orders |
| POST | `/api/orders` | Create order |
| GET | `/api/orders/{id}` | Get order with line items |
| PUT | `/api/orders/{id}` | Update customer, datetime, or discount |
| DELETE | `/api/orders/{id}` | Delete order and restore stock |
| GET | `/api/order-details?order_id=1` | List order line items (optional order filter) |
| POST | `/api/order-details` | Add line item and reduce stock |
| GET | `/api/order-details/{id}` | Get line item |
| PUT | `/api/order-details/{id}` | Change order, product, or quantity |
| DELETE | `/api/order-details/{id}` | Remove line item and restore stock |
| GET | `/api/dashboard/summary` | Dashboard metrics and lists |

## Example CRUD requests

Use Swagger UI at `/docs` for interactive requests. Examples below use JSON bodies.

### Create customer

```json
{
  "customer_name": "Aarav Shah",
  "customer_contact": "9876543210",
  "customer_gender": "Male"
}
```

### Create product

```json
{
  "product_image": "https://example.com/headphones.jpg",
  "product_name": "Wireless Headphones",
  "product_stock": 25,
  "product_price": "2499.00"
}
```

### Create order

```json
{
  "customer_id": 1,
  "order_datetime": "2026-10-09T10:30:00",
  "discount": "0.00"
}
```

### Add line item

```json
{
  "order_id": 1,
  "product_id": 1,
  "quantity": 2
}
```

The API reads product price for the line item automatically; do not send `unit_price` or `total_price`. Once the order has a subtotal, update its discount if required:

```json
{
  "customer_id": 1,
  "order_datetime": "2026-10-09T10:30:00",
  "discount": "100.00"
}
```

### Update line item quantity

```json
{
  "order_id": 1,
  "product_id": 1,
  "quantity": 3
}
```

### Delete a record

Send `DELETE /api/customers/1`, `DELETE /api/products/1`, `DELETE /api/orders/1`, or `DELETE /api/order-details/1`. Deletion may return HTTP 409 when a business rule prevents it.

## Troubleshooting

**`connection refused` / PostgreSQL connection error**

- Confirm the PostgreSQL Windows service is running.
- Check database name, port (usually `5432`), username, and password in `backend/.env`.
- Confirm the `ecommerce_db` database exists and that you executed the schema against that database.
- Test in pgAdmin or with `psql` before starting FastAPI.

**`ModuleNotFoundError` in FastAPI**

- Activate the backend virtual environment from the `backend` directory.
- Run `pip install -r requirements.txt` again.
- Start the app from `backend` using `uvicorn app.main:app --reload` (not from inside `backend/app`).

**CORS or connection errors in the browser**

- Start FastAPI on port `8000` and Angular on `4200`.
- Make sure `CORS_ORIGINS=http://localhost:4200` is in `backend/.env` and restart Uvicorn after editing it.
- Use the API URL from `frontend/src/environments/environment.ts` consistently.

**`relation does not exist` / schema mismatch**

- Connect to `ecommerce_db`, then run the schema file.
- If tables already existed with a different schema, compare their columns and constraints with `database/schema.sql`; apply a reviewed migration instead of dropping/recreating tables.

**Angular styles do not load**

- Confirm `.postcssrc.json` exists in `frontend` and `src/styles.css` begins with `@import "tailwindcss";`.
- Run `npm install` and restart `npx ng serve`.

## Notes

- No authentication is included, as specified. Do not expose this development server directly to the public internet.
- All dashboard values come from PostgreSQL; the UI does not hardcode dashboard statistics.
- Backend source is complete but the database connection and full browser workflow depend on your local PostgreSQL, Python, Node.js, and npm setup.
