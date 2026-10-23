"""Reports and analytics routes."""
import datetime
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Sale, SaleItem, Product, Category, Customer, PurchaseOrder
from auth import get_current_user

router = APIRouter(prefix="/reports")
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def reports_page(
    request: Request,
    report_type: str = Query("sales", alias="type"),
    period: str = Query("30", alias="period"),
    db: Session = Depends(get_db)
):
    """Reports and analytics page."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    days = int(period)
    start_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)

    report_data = {}

    if report_type == "sales":
        # Daily sales for the period
        daily_sales = []
        today = datetime.datetime.utcnow().date()
        for i in range(days - 1, -1, -1):
            day = today - datetime.timedelta(days=i)
            day_start = datetime.datetime.combine(day, datetime.time.min)
            day_end = datetime.datetime.combine(day, datetime.time.max)
            day_total = db.query(func.sum(Sale.total_amount)).filter(
                Sale.created_at.between(day_start, day_end),
                Sale.status == "completed"
            ).scalar() or 0
            day_count = db.query(Sale).filter(
                Sale.created_at.between(day_start, day_end),
                Sale.status == "completed"
            ).count()
            daily_sales.append({
                "date": day.strftime("%Y-%m-%d"),
                "display_date": day.strftime("%b %d"),
                "total": round(float(day_total), 2),
                "count": day_count
            })

        total_revenue = sum(d["total"] for d in daily_sales)
        total_orders = sum(d["count"] for d in daily_sales)
        avg_order = total_revenue / total_orders if total_orders else 0

        # Payment method breakdown
        payment_methods = db.query(
            Sale.payment_method,
            func.count(Sale.id),
            func.sum(Sale.total_amount)
        ).filter(
            Sale.created_at >= start_date, Sale.status == "completed"
        ).group_by(Sale.payment_method).all()

        report_data = {
            "daily_sales": daily_sales,
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "avg_order": round(avg_order, 2),
            "payment_methods": payment_methods,
        }

    elif report_type == "products":
        # Top selling products
        top_products = db.query(
            Product.name, Product.sku,
            func.sum(SaleItem.quantity).label("total_qty"),
            func.sum(SaleItem.total_price).label("total_revenue")
        ).join(SaleItem, Product.id == SaleItem.product_id)\
         .join(Sale, SaleItem.sale_id == Sale.id)\
         .filter(Sale.created_at >= start_date, Sale.status == "completed")\
         .group_by(Product.id)\
         .order_by(func.sum(SaleItem.total_price).desc())\
         .limit(20).all()

        # Slow-moving products (no sales)
        sold_product_ids = db.query(SaleItem.product_id).join(Sale).filter(
            Sale.created_at >= start_date, Sale.status == "completed"
        ).distinct().subquery()
        slow_products = db.query(Product).filter(
            Product.is_active == True,
            ~Product.id.in_(sold_product_ids)
        ).order_by(Product.name).all()

        # Category performance
        category_perf = db.query(
            Category.name,
            func.sum(SaleItem.quantity).label("total_qty"),
            func.sum(SaleItem.total_price).label("total_revenue")
        ).join(Product, Category.id == Product.category_id)\
         .join(SaleItem, Product.id == SaleItem.product_id)\
         .join(Sale, SaleItem.sale_id == Sale.id)\
         .filter(Sale.created_at >= start_date, Sale.status == "completed")\
         .group_by(Category.name)\
         .order_by(func.sum(SaleItem.total_price).desc())\
         .all()

        report_data = {
            "top_products": top_products,
            "slow_products": slow_products,
            "category_perf": category_perf,
        }

    elif report_type == "inventory":
        # Inventory overview
        total_items = db.query(func.sum(Product.quantity)).filter(Product.is_active == True).scalar() or 0
        total_value = db.query(func.sum(Product.cost_price * Product.quantity)).filter(
            Product.is_active == True
        ).scalar() or 0
        total_retail = db.query(func.sum(Product.selling_price * Product.quantity)).filter(
            Product.is_active == True
        ).scalar() or 0

        low_stock = db.query(Product).filter(
            Product.is_active == True,
            Product.quantity <= Product.min_stock
        ).order_by(Product.quantity).all()

        out_of_stock = db.query(Product).filter(
            Product.is_active == True,
            Product.quantity == 0
        ).all()

        # Stock by category
        stock_by_cat = db.query(
            Category.name,
            func.count(Product.id),
            func.sum(Product.quantity),
            func.sum(Product.cost_price * Product.quantity)
        ).join(Product, Category.id == Product.category_id)\
         .filter(Product.is_active == True)\
         .group_by(Category.name)\
         .order_by(func.sum(Product.cost_price * Product.quantity).desc())\
         .all()

        report_data = {
            "total_items": int(total_items),
            "total_value": round(float(total_value), 2),
            "total_retail": round(float(total_retail), 2),
            "potential_profit": round(float(total_retail - total_value), 2),
            "low_stock": low_stock,
            "out_of_stock": out_of_stock,
            "stock_by_category": stock_by_cat,
        }

    elif report_type == "customers":
        # Top customers
        top_customers = db.query(
            Customer.name, Customer.phone,
            func.count(Sale.id).label("order_count"),
            func.sum(Sale.total_amount).label("total_spent")
        ).join(Sale, Customer.id == Sale.customer_id)\
         .filter(Sale.created_at >= start_date, Sale.status == "completed")\
         .group_by(Customer.id)\
         .order_by(func.sum(Sale.total_amount).desc())\
         .limit(20).all()

        report_data = {
            "top_customers": top_customers,
        }

    return templates.TemplateResponse("reports.html", {
        "request": request,
        "user": user,
        "report_type": report_type,
        "period": period,
        "report_data": report_data,
    })
