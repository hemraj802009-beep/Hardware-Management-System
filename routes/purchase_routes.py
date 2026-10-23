"""Purchase Order management routes."""
import datetime
from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import PurchaseOrder, PurchaseItem, Supplier, Product
from auth import get_current_user

router = APIRouter(prefix="/purchases")
templates = Jinja2Templates(directory="templates")


def _generate_po_number(db: Session) -> str:
    """Generate next PO number."""
    last = db.query(PurchaseOrder).order_by(PurchaseOrder.id.desc()).first()
    if last and last.po_number.startswith("PO-"):
        try:
            num = int(last.po_number.split("-")[1]) + 1
        except (ValueError, IndexError):
            num = 501
    else:
        num = 501
    return f"PO-{num}"


@router.get("/")
async def list_purchases(
    request: Request,
    status: str = Query("all"),
    db: Session = Depends(get_db)
):
    """List purchase orders."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    query = db.query(PurchaseOrder).options(
        joinedload(PurchaseOrder.supplier),
        joinedload(PurchaseOrder.items).joinedload(PurchaseItem.product)
    )

    if status != "all":
        query = query.filter(PurchaseOrder.status == status)

    purchases = query.order_by(PurchaseOrder.created_at.desc()).all()

    return templates.TemplateResponse("purchases.html", {
        "request": request,
        "user": user,
        "purchases": purchases,
        "status_filter": status,
    })


@router.get("/add")
async def add_purchase_page(request: Request, db: Session = Depends(get_db)):
    """Show add purchase order form."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    suppliers = db.query(Supplier).filter(Supplier.is_active == True).order_by(Supplier.name).all()
    products = db.query(Product).filter(Product.is_active == True).order_by(Product.name).all()

    return templates.TemplateResponse("purchase_form.html", {
        "request": request,
        "user": user,
        "suppliers": suppliers,
        "products": products,
        "purchase": None,
        "title": "Create Purchase Order",
        "po_number": _generate_po_number(db),
    })


@router.post("/add")
async def add_purchase(
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a purchase order from form data."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    form = await request.form()
    supplier_id = int(form.get("supplier_id", 0))
    notes = form.get("notes", "")
    expected_date_str = form.get("expected_date", "")

    expected_date = None
    if expected_date_str:
        try:
            expected_date = datetime.datetime.strptime(expected_date_str, "%Y-%m-%d")
        except ValueError:
            pass

    # Parse items from form
    items = []
    total = 0
    i = 0
    while True:
        product_id = form.get(f"items[{i}][product_id]")
        if product_id is None:
            break
        quantity = int(form.get(f"items[{i}][quantity]", 0))
        unit_cost = float(form.get(f"items[{i}][unit_cost]", 0))
        item_total = quantity * unit_cost
        total += item_total
        items.append(PurchaseItem(
            product_id=int(product_id),
            quantity=quantity,
            unit_cost=unit_cost,
            total_cost=item_total
        ))
        i += 1

    if not items:
        return RedirectResponse(url="/purchases/add", status_code=302)

    po = PurchaseOrder(
        po_number=_generate_po_number(db),
        supplier_id=supplier_id,
        user_id=user["user_id"],
        total_amount=total,
        status="ordered",
        notes=notes,
        expected_date=expected_date,
        items=items
    )
    db.add(po)
    db.commit()
    return RedirectResponse(url="/purchases", status_code=302)


@router.get("/receive/{po_id}")
async def receive_purchase(request: Request, po_id: int, db: Session = Depends(get_db)):
    """Mark a purchase order as received and update stock."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    po = db.query(PurchaseOrder).options(
        joinedload(PurchaseOrder.items)
    ).filter(PurchaseOrder.id == po_id).first()

    if po and po.status == "ordered":
        po.status = "received"
        po.received_date = datetime.datetime.utcnow()
        # Update stock
        for item in po.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.quantity += item.quantity
        db.commit()

    return RedirectResponse(url="/purchases", status_code=302)


@router.get("/cancel/{po_id}")
async def cancel_purchase(request: Request, po_id: int, db: Session = Depends(get_db)):
    """Cancel a purchase order."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if po and po.status == "ordered":
        po.status = "cancelled"
        db.commit()

    return RedirectResponse(url="/purchases", status_code=302)


@router.get("/view/{po_id}")
async def view_purchase(request: Request, po_id: int, db: Session = Depends(get_db)):
    """View purchase order details."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    po = db.query(PurchaseOrder).options(
        joinedload(PurchaseOrder.supplier),
        joinedload(PurchaseOrder.items).joinedload(PurchaseItem.product)
    ).filter(PurchaseOrder.id == po_id).first()

    if not po:
        return RedirectResponse(url="/purchases", status_code=302)

    return templates.TemplateResponse("purchase_view.html", {
        "request": request,
        "user": user,
        "purchase": po,
    })
