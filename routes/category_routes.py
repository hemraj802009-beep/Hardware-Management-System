"""Category management routes."""
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Category, Product
from auth import get_current_user

router = APIRouter(prefix="/categories")
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def list_categories(request: Request, db: Session = Depends(get_db)):
    """List all categories."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    categories = db.query(
        Category,
        func.count(Product.id).label("product_count")
    ).outerjoin(Product, (Product.category_id == Category.id) & (Product.is_active == True))\
     .group_by(Category.id)\
     .order_by(Category.name).all()

    return templates.TemplateResponse("categories.html", {
        "request": request,
        "user": user,
        "categories": categories,
    })


@router.post("/add")
async def add_category(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    icon: str = Form("fas fa-box"),
    db: Session = Depends(get_db)
):
    """Add a new category."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    existing = db.query(Category).filter(Category.name == name).first()
    if not existing:
        category = Category(name=name, description=description, icon=icon)
        db.add(category)
        db.commit()
    return RedirectResponse(url="/categories", status_code=302)


@router.post("/edit/{category_id}")
async def edit_category(
    request: Request,
    category_id: int,
    name: str = Form(...),
    description: str = Form(""),
    icon: str = Form("fas fa-box"),
    db: Session = Depends(get_db)
):
    """Update a category."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    category = db.query(Category).filter(Category.id == category_id).first()
    if category:
        category.name = name
        category.description = description
        category.icon = icon
        db.commit()
    return RedirectResponse(url="/categories", status_code=302)


@router.get("/delete/{category_id}")
async def delete_category(request: Request, category_id: int, db: Session = Depends(get_db)):
    """Delete a category (only if no products)."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    product_count = db.query(Product).filter(
        Product.category_id == category_id, Product.is_active == True
    ).count()
    if product_count == 0:
        category = db.query(Category).filter(Category.id == category_id).first()
        if category:
            db.delete(category)
            db.commit()
    return RedirectResponse(url="/categories", status_code=302)
