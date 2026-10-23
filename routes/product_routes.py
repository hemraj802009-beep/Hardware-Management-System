"""Product management routes."""
import datetime
from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Product, Category, Supplier
from auth import get_current_user

router = APIRouter(prefix="/products")
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def list_products(
    request: Request,
    search: str = Query("", alias="q"),
    category_id: int = Query(0, alias="cat"),
    stock_filter: str = Query("all", alias="stock"),
    db: Session = Depends(get_db)
):
    """List all products with filtering."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    query = db.query(Product).options(
        joinedload(Product.category),
        joinedload(Product.supplier)
    ).filter(Product.is_active == True)

    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.sku.ilike(f"%{search}%"))
        )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if stock_filter == "low":
        query = query.filter(Product.quantity <= Product.min_stock)
    elif stock_filter == "out":
        query = query.filter(Product.quantity == 0)

    products = query.order_by(Product.name).all()
    categories = db.query(Category).order_by(Category.name).all()

    return templates.TemplateResponse("products.html", {
        "request": request,
        "user": user,
        "products": products,
        "categories": categories,
        "search": search,
        "category_id": category_id,
        "stock_filter": stock_filter,
    })


@router.get("/add")
async def add_product_page(request: Request, db: Session = Depends(get_db)):
    """Show add product form."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    categories = db.query(Category).order_by(Category.name).all()
    suppliers = db.query(Supplier).filter(Supplier.is_active == True).order_by(Supplier.name).all()

    return templates.TemplateResponse("product_form.html", {
        "request": request,
        "user": user,
        "product": None,
        "categories": categories,
        "suppliers": suppliers,
        "title": "Add New Product",
    })


@router.post("/add")
async def add_product(
    request: Request,
    name: str = Form(...),
    sku: str = Form(...),
    description: str = Form(""),
    category_id: int = Form(0),
    supplier_id: int = Form(0),
    cost_price: float = Form(0.0),
    selling_price: float = Form(0.0),
    quantity: int = Form(0),
    min_stock: int = Form(5),
    location: str = Form(""),
    unit: str = Form("piece"),
    db: Session = Depends(get_db)
):
    """Create a new product."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Check if SKU exists
    existing = db.query(Product).filter(Product.sku == sku).first()
    if existing:
        categories = db.query(Category).order_by(Category.name).all()
        suppliers = db.query(Supplier).filter(Supplier.is_active == True).order_by(Supplier.name).all()
        return templates.TemplateResponse("product_form.html", {
            "request": request,
            "user": user,
            "product": None,
            "categories": categories,
            "suppliers": suppliers,
            "title": "Add New Product",
            "error": f"SKU '{sku}' already exists",
        })

    product = Product(
        name=name, sku=sku, description=description,
        category_id=category_id if category_id else None,
        supplier_id=supplier_id if supplier_id else None,
        cost_price=cost_price, selling_price=selling_price,
        quantity=quantity, min_stock=min_stock,
        location=location, unit=unit
    )
    db.add(product)
    db.commit()
    return RedirectResponse(url="/products", status_code=302)


@router.get("/edit/{product_id}")
async def edit_product_page(request: Request, product_id: int, db: Session = Depends(get_db)):
    """Show edit product form."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return RedirectResponse(url="/products", status_code=302)

    categories = db.query(Category).order_by(Category.name).all()
    suppliers = db.query(Supplier).filter(Supplier.is_active == True).order_by(Supplier.name).all()

    return templates.TemplateResponse("product_form.html", {
        "request": request,
        "user": user,
        "product": product,
        "categories": categories,
        "suppliers": suppliers,
        "title": "Edit Product",
    })


@router.post("/edit/{product_id}")
async def edit_product(
    request: Request,
    product_id: int,
    name: str = Form(...),
    sku: str = Form(...),
    description: str = Form(""),
    category_id: int = Form(0),
    supplier_id: int = Form(0),
    cost_price: float = Form(0.0),
    selling_price: float = Form(0.0),
    quantity: int = Form(0),
    min_stock: int = Form(5),
    location: str = Form(""),
    unit: str = Form("piece"),
    db: Session = Depends(get_db)
):
    """Update an existing product."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return RedirectResponse(url="/products", status_code=302)

    # Check SKU uniqueness
    existing = db.query(Product).filter(Product.sku == sku, Product.id != product_id).first()
    if existing:
        categories = db.query(Category).order_by(Category.name).all()
        suppliers = db.query(Supplier).filter(Supplier.is_active == True).order_by(Supplier.name).all()
        return templates.TemplateResponse("product_form.html", {
            "request": request,
            "user": user,
            "product": product,
            "categories": categories,
            "suppliers": suppliers,
            "title": "Edit Product",
            "error": f"SKU '{sku}' already exists for another product",
        })

    product.name = name
    product.sku = sku
    product.description = description
    product.category_id = category_id if category_id else None
    product.supplier_id = supplier_id if supplier_id else None
    product.cost_price = cost_price
    product.selling_price = selling_price
    product.quantity = quantity
    product.min_stock = min_stock
    product.location = location
    product.unit = unit
    product.updated_at = datetime.datetime.utcnow()

    db.commit()
    return RedirectResponse(url="/products", status_code=302)


@router.get("/delete/{product_id}")
async def delete_product(request: Request, product_id: int, db: Session = Depends(get_db)):
    """Soft-delete a product."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.is_active = False
        db.commit()
    return RedirectResponse(url="/products", status_code=302)
