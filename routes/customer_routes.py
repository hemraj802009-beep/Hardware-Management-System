"""Customer management routes."""
from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Customer, Sale
from auth import get_current_user

router = APIRouter(prefix="/customers")
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def list_customers(
    request: Request,
    search: str = Query("", alias="q"),
    db: Session = Depends(get_db)
):
    """List all customers."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    query = db.query(
        Customer,
        func.count(Sale.id).label("total_orders"),
        func.coalesce(func.sum(Sale.total_amount), 0).label("total_spent")
    ).outerjoin(Sale, (Sale.customer_id == Customer.id) & (Sale.status == "completed"))

    if search:
        query = query.filter(
            (Customer.name.ilike(f"%{search}%")) |
            (Customer.phone.ilike(f"%{search}%")) |
            (Customer.city.ilike(f"%{search}%"))
        )

    customers = query.filter(Customer.is_active == True)\
        .group_by(Customer.id)\
        .order_by(Customer.name).all()

    return templates.TemplateResponse("customers.html", {
        "request": request,
        "user": user,
        "customers": customers,
        "search": search,
    })


@router.get("/add")
async def add_customer_page(request: Request):
    """Show add customer form."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse("customer_form.html", {
        "request": request,
        "user": user,
        "customer": None,
        "title": "Add Customer",
    })


@router.post("/add")
async def add_customer(
    request: Request,
    name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    city: str = Form(""),
    db: Session = Depends(get_db)
):
    """Create a customer."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    customer = Customer(name=name, email=email, phone=phone, address=address, city=city)
    db.add(customer)
    db.commit()
    return RedirectResponse(url="/customers", status_code=302)


@router.get("/edit/{customer_id}")
async def edit_customer_page(request: Request, customer_id: int, db: Session = Depends(get_db)):
    """Show edit customer form."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        return RedirectResponse(url="/customers", status_code=302)

    return templates.TemplateResponse("customer_form.html", {
        "request": request,
        "user": user,
        "customer": customer,
        "title": "Edit Customer",
    })


@router.post("/edit/{customer_id}")
async def edit_customer(
    request: Request,
    customer_id: int,
    name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    city: str = Form(""),
    db: Session = Depends(get_db)
):
    """Update a customer."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        customer.name = name
        customer.email = email
        customer.phone = phone
        customer.address = address
        customer.city = city
        db.commit()
    return RedirectResponse(url="/customers", status_code=302)


@router.get("/delete/{customer_id}")
async def delete_customer(request: Request, customer_id: int, db: Session = Depends(get_db)):
    """Soft-delete a customer."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        customer.is_active = False
        db.commit()
    return RedirectResponse(url="/customers", status_code=302)
