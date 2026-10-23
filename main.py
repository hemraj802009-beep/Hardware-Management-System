"""Hardware Store Management System - Main Application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from database import init_db, SessionLocal
from seed import seed_database
from routes import (
    auth_routes,
    dashboard_routes,
    product_routes,
    category_routes,
    supplier_routes,
    customer_routes,
    sales_routes,
    purchase_routes,
    report_routes,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed data on startup."""
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(title="HardwareHub - Store Management System", version="1.0.0", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include all routers
app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(product_routes.router)
app.include_router(category_routes.router)
app.include_router(supplier_routes.router)
app.include_router(customer_routes.router)
app.include_router(sales_routes.router)
app.include_router(purchase_routes.router)
app.include_router(report_routes.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

