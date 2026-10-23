"""Supplier management routes."""
from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Supplier, Product
from auth import get_current_user

router = APIRouter(prefix="/suppliers")
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def list_suppliers(
    request: Request,
    search: str = Query("", alias="q"),
    db: Session = Depends(get_db)
):
    """List all suppliers."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    query = db.query(
        Supplier,
        func.count(Product.id).label("product_count")
    ).outerjoin(Product, (Product.supplier_id == Supplier.id) & (Product.is_active == True))

    if search:
        query = query.filter(
            (Supplier.name.ilike(f"%{search}%")) |
            (Supplier.contact_person.ilike(f"%{search}%")) |
            (Supplier.city.ilike(f"%{search}%"))
        )

    suppliers = query.filter(Supplier.is_active == True)\
        .group_by(Supplier.id)\
        .order_by(Supplier.name).all()

    return templates.TemplateResponse("suppliers.html", {
        "request": request,
        "user": user,
        "suppliers": suppliers,
        "search": search,
    })


@router.get("/add")
async def add_supplier_page(request: Request, db: Session = Depends(get_db)):
    """Show add supplier form."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse("supplier_form.html", {
        "request": request,
        "user": user,
        "supplier": None,
        "title": "Add Supplier",
    })


@router.post("/add")
async def add_supplier(
    request: Request,
    name: str = Form(...),
    contact_person: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    city: str = Form(""),
    db: Session = Depends(get_db)
):
    """Create a supplier."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    supplier = Supplier(
        name=name, contact_person=contact_person, email=email,
        phone=phone, address=address, city=city
    )
    db.add(supplier)
    db.commit()
    return RedirectResponse(url="/suppliers", status_code=302)


@router.get("/edit/{supplier_id}")
async def edit_supplier_page(request: Request, supplier_id: int, db: Session = Depends(get_db)):
    """Show edit supplier form."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        return RedirectResponse(url="/suppliers", status_code=302)

    return templates.TemplateResponse("supplier_form.html", {
        "request": request,
        "user": user,
        "supplier": supplier,
        "title": "Edit Supplier",
    })


@router.post("/edit/{supplier_id}")
async def edit_supplier(
    request: Request,
    supplier_id: int,
    name: str = Form(...),
    contact_person: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
    city: str = Form(""),
    db: Session = Depends(get_db)
):
    """Update a supplier."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if supplier:
        supplier.name = name
        supplier.contact_person = contact_person
        supplier.email = email
        supplier.phone = phone
        supplier.address = address
        supplier.city = city
        db.commit()
    return RedirectResponse(url="/suppliers", status_code=302)


@router.get("/delete/{supplier_id}")
async def delete_supplier(request: Request, supplier_id: int, db: Session = Depends(get_db)):
    """Soft-delete a supplier."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if supplier:
        supplier.is_active = False
        db.commit()
    return RedirectResponse(url="/suppliers", status_code=302)
