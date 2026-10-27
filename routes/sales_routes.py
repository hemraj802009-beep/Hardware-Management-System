"""Sales and POS routes."""
import datetime
from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from database import get_db
from models import Sale, SaleItem, Product, Customer
from auth import get_current_user

router = APIRouter(prefix="/sales")
templates = Jinja2Templates(directory="templates")


def _generate_invoice_number(db: Session) -> str:
    """Generate the next invoice number."""
    last_sale = db.query(Sale).order_by(Sale.id.desc()).first()
    if last_sale and last_sale.invoice_number.startswith("INV-"):
        try:
            num = int(last_sale.invoice_number.split("-")[1]) + 1
        except (ValueError, IndexError):
            num = 1001
    else:
        num = 1001
    return f"INV-{num}"


@router.get("/")
async def list_sales(
    request: Request,
    search: str = Query("", alias="q"),
    status: str = Query("all"),
    db: Session = Depends(get_db)
):
    """List all sales."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    query = db.query(Sale).options(
        joinedload(Sale.customer),
        joinedload(Sale.items).joinedload(SaleItem.product)
    )

    if search:
        query = query.filter(
            (Sale.invoice_number.ilike(f"%{search}%"))
        )
    if status != "all":
        query = query.filter(Sale.status == status)

    sales = query.order_by(Sale.created_at.desc()).limit(100).all()

    return templates.TemplateResponse("sales.html", {
        "request": request,
        "user": user,
        "sales": sales,
        "search": search,
        "status_filter": status,
    })


@router.get("/pos")
async def pos_page(request: Request, db: Session = Depends(get_db)):
    """Point of Sale page."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    products = db.query(Product).filter(
        Product.is_active == True, Product.quantity > 0
    ).order_by(Product.name).all()
    customers = db.query(Customer).filter(Customer.is_active == True).order_by(Customer.name).all()

    return templates.TemplateResponse("pos.html", {
        "request": request,
        "user": user,
        "products": products,
        "customers": customers,
    })


@router.get("/api/products")
async def api_search_products(
    request: Request,
    q: str = Query(""),
    db: Session = Depends(get_db)
):
    """API endpoint for product search in POS."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(content=[], status_code=401)

    query = db.query(Product).filter(Product.is_active == True, Product.quantity > 0)
    if q:
        query = query.filter(
            (Product.name.ilike(f"%{q}%")) | (Product.sku.ilike(f"%{q}%"))
        )
    products = query.limit(20).all()
    return JSONResponse(content=[{
        "id": p.id, "name": p.name, "sku": p.sku,
        "price": p.selling_price, "quantity": p.quantity,
        "unit": p.unit
    } for p in products])


@router.post("/pos/checkout")
async def pos_checkout(
    request: Request,
    db: Session = Depends(get_db)
):
    """Process POS checkout."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)

    data = await request.json()
    items = data.get("items", [])
    customer_id = data.get("customer_id")
    payment_method = data.get("payment_method", "cash")
    discount_pct = data.get("discount", 0)
    notes = data.get("notes", "")

    if not items:
        return JSONResponse(content={"error": "No items in cart"}, status_code=400)

    # Validate stock and create sale items
    sale_items = []
    subtotal = 0
    for item in items:
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if not product:
            return JSONResponse(content={"error": f"Product not found"}, status_code=400)
        if product.quantity < item["quantity"]:
            return JSONResponse(
                content={"error": f"Insufficient stock for {product.name}. Available: {product.quantity}"},
                status_code=400
            )

        item_total = item["quantity"] * product.selling_price
        subtotal += item_total
        sale_items.append(SaleItem(
            product_id=product.id,
            quantity=item["quantity"],
            unit_price=product.selling_price,
            total_price=item_total
        ))
        # Reduce stock
        product.quantity -= item["quantity"]

    tax = round(subtotal * 0.18, 2)
    discount_amt = round(subtotal * (discount_pct / 100), 2)
    total = round(subtotal + tax - discount_amt, 2)

    sale = Sale(
        invoice_number=_generate_invoice_number(db),
        customer_id=customer_id if customer_id else None,
        user_id=user["user_id"],
        subtotal=subtotal,
        tax_amount=tax,
        discount_amount=discount_amt,
        total_amount=total,
        payment_method=payment_method,
        status="completed",
        notes=notes,
        items=sale_items
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)

    # Prepare WhatsApp/invoice link if customer has phone
    whatsapp_link = None
    if sale.customer_id:
        customer = db.query(Customer).filter(Customer.id == sale.customer_id).first()
        if customer and customer.phone:
            # Clean phone number (remove spaces, +, etc.)
            phone = ''.join(filter(str.isdigit, customer.phone))
            if phone:
                # Create invoice link
                invoice_url = f"/sales/view/{sale.id}"
                message = f"Hello {customer.name}, your invoice {sale.invoice_number} of ₹{sale.total_amount:.2f} is ready. View it here: {invoice_url}"
                import urllib.parse
                whatsapp_link = f"https://wa.me/{phone}?text={urllib.parse.quote(message)}"

    return JSONResponse(content={
        "success": True,
        "invoice_number": sale.invoice_number,
        "total": sale.total_amount,
        "sale_id": sale.id,
        "whatsapp_link": whatsapp_link,
        "customer_phone": customer.phone if 'customer' in locals() and customer and customer.phone else None
    })


@router.get("/view/{sale_id}")
async def view_sale(request: Request, sale_id: int, db: Session = Depends(get_db)):
    """View sale details / invoice."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    sale = db.query(Sale).options(
        joinedload(Sale.customer),
        joinedload(Sale.items).joinedload(SaleItem.product)
    ).filter(Sale.id == sale_id).first()

    if not sale:
        return RedirectResponse(url="/sales", status_code=302)

    return templates.TemplateResponse("invoice.html", {
        "request": request,
        "user": user,
        "sale": sale,
    })


@router.get("/send-whatsapp/{sale_id}")
async def send_invoice_whatsapp(request: Request, sale_id: int, db: Session = Depends(get_db)):
    """Send invoice link via WhatsApp to customer."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    sale = db.query(Sale).options(joinedload(Sale.customer)).filter(Sale.id == sale_id).first()
    if not sale:
        return RedirectResponse(url="/sales", status_code=302)

    whatsapp_link = None
    if sale.customer and sale.customer.phone:
        phone = ''.join(filter(str.isdigit, sale.customer.phone))
        if phone:
            invoice_url = f"/sales/view/{sale.id}"
            message = f"Hello {sale.customer.name}, your invoice {sale.invoice_number} of ₹{sale.total_amount:.2f} is ready. View it here: {invoice_url}"
            import urllib.parse
            whatsapp_link = f"https://wa.me/{phone}?text={urllib.parse.quote(message)}"
            return RedirectResponse(url=whatsapp_link, status_code=302)

    return RedirectResponse(url=f"/sales/view/{sale_id}", status_code=302)


@router.get("/cancel/{sale_id}")
async def cancel_sale(request: Request, sale_id: int, db: Session = Depends(get_db)):
    """Cancel a sale and restore stock."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    sale = db.query(Sale).options(joinedload(Sale.items)).filter(Sale.id == sale_id).first()
    if sale and sale.status == "completed":
        sale.status = "cancelled"
        # Restore stock
        for item in sale.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.quantity += item.quantity
        db.commit()

    return RedirectResponse(url="/sales", status_code=302)
