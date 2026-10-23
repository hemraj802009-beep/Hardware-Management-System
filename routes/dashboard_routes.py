"""Dashboard routes."""
import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Product, Sale, SaleItem, Customer, PurchaseOrder, Category
from auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Render main dashboard."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Key metrics
    total_products = db.query(Product).filter(Product.is_active == True).count()
    total_customers = db.query(Customer).filter(Customer.is_active == True).count()

    # Today's sales
    today = datetime.datetime.utcnow().date()
    today_start = datetime.datetime.combine(today, datetime.time.min)
    today_end = datetime.datetime.combine(today, datetime.time.max)
    today_sales = db.query(func.sum(Sale.total_amount)).filter(
        Sale.created_at.between(today_start, today_end),
        Sale.status == "completed"
    ).scalar() or 0
    today_orders = db.query(Sale).filter(
        Sale.created_at.between(today_start, today_end),
        Sale.status == "completed"
    ).count()

    # Monthly sales
    month_start = today.replace(day=1)
    month_start_dt = datetime.datetime.combine(month_start, datetime.time.min)
    monthly_sales = db.query(func.sum(Sale.total_amount)).filter(
        Sale.created_at >= month_start_dt,
        Sale.status == "completed"
    ).scalar() or 0

    # Low stock products
    low_stock = db.query(Product).filter(
        Product.is_active == True,
        Product.quantity <= Product.min_stock
    ).all()

    # Pending purchase orders
    pending_po = db.query(PurchaseOrder).filter(
        PurchaseOrder.status == "ordered"
    ).count()

    # Revenue by category (last 30 days)
    thirty_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    category_revenue_rows = db.query(
        Category.name,
        func.sum(SaleItem.total_price)
    ).join(Product, SaleItem.product_id == Product.id)\
     .join(Category, Product.category_id == Category.id)\
     .join(Sale, SaleItem.sale_id == Sale.id)\
     .filter(Sale.created_at >= thirty_days_ago, Sale.status == "completed")\
     .group_by(Category.name)\
     .order_by(func.sum(SaleItem.total_price).desc())\
     .all()
    category_revenue = [[r[0], round(float(r[1] or 0), 2)] for r in category_revenue_rows]

    # Daily sales for chart (last 7 days)
    daily_sales = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_start = datetime.datetime.combine(day, datetime.time.min)
        day_end = datetime.datetime.combine(day, datetime.time.max)
        day_total = db.query(func.sum(Sale.total_amount)).filter(
            Sale.created_at.between(day_start, day_end),
            Sale.status == "completed"
        ).scalar() or 0
        daily_sales.append({
            "date": day.strftime("%b %d"),
            "total": round(float(day_total), 2)
        })

    # Recent sales
    recent_sales = db.query(Sale).order_by(Sale.created_at.desc()).limit(5).all()

    # Top selling products (last 30 days)
    top_products = db.query(
        Product.name,
        func.sum(SaleItem.quantity).label("total_qty"),
        func.sum(SaleItem.total_price).label("total_revenue")
    ).join(SaleItem, Product.id == SaleItem.product_id)\
     .join(Sale, SaleItem.sale_id == Sale.id)\
     .filter(Sale.created_at >= thirty_days_ago, Sale.status == "completed")\
     .group_by(Product.name)\
     .order_by(func.sum(SaleItem.total_price).desc())\
     .limit(5).all()

    # Total inventory value
    inventory_value = db.query(
        func.sum(Product.cost_price * Product.quantity)
    ).filter(Product.is_active == True).scalar() or 0

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "total_products": total_products,
        "total_customers": total_customers,
        "today_sales": round(float(today_sales), 2),
        "today_orders": today_orders,
        "monthly_sales": round(float(monthly_sales), 2),
        "low_stock": low_stock,
        "low_stock_count": len(low_stock),
        "pending_po": pending_po,
        "category_revenue": category_revenue,
        "daily_sales": daily_sales,
        "recent_sales": recent_sales,
        "top_products": top_products,
        "inventory_value": round(float(inventory_value), 2),
    })
