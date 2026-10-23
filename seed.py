"""Seed the database with initial data."""
import datetime
import random
from sqlalchemy.orm import Session
from models import (
    User, Category, Supplier, Product, Customer, Sale, SaleItem,
    PurchaseOrder, PurchaseItem
)
from auth import hash_password


def seed_database(db: Session):
    """Populate database with sample data if empty."""
    # Check if already seeded
    if db.query(User).count() > 0:
        return

    # --- Users ---
    admin = User(
        username="admin",
        email="admin@hwstore.com",
        hashed_password=hash_password("admin123"),
        full_name="Store Admin",
        role="admin"
    )
    staff = User(
        username="staff",
        email="staff@hwstore.com",
        hashed_password=hash_password("staff123"),
        full_name="John Doe",
        role="staff"
    )
    db.add_all([admin, staff])
    db.flush()

    # --- Categories ---
    categories_data = [
        ("Power Tools", "Electric and battery-powered tools", "fas fa-bolt"),
        ("Hand Tools", "Manual tools and equipment", "fas fa-wrench"),
        ("Plumbing", "Pipes, fittings, and plumbing supplies", "fas fa-faucet"),
        ("Electrical", "Wires, switches, and electrical supplies", "fas fa-plug"),
        ("Paint & Supplies", "Paints, brushes, and painting accessories", "fas fa-paint-roller"),
        ("Fasteners", "Screws, nails, bolts, and anchors", "fas fa-cog"),
        ("Safety Equipment", "PPE and safety gear", "fas fa-hard-hat"),
        ("Garden & Outdoor", "Garden tools and outdoor equipment", "fas fa-leaf"),
        ("Building Materials", "Cement, sand, bricks, and more", "fas fa-building"),
        ("Adhesives & Sealants", "Glues, tapes, and sealants", "fas fa-tape"),
    ]
    categories = []
    for name, desc, icon in categories_data:
        cat = Category(name=name, description=desc, icon=icon)
        categories.append(cat)
    db.add_all(categories)
    db.flush()

    # --- Suppliers ---
    suppliers_data = [
        ("Bosch India Ltd.", "Rajesh Kumar", "rajesh@bosch.in", "+91-9876543210", "Bangalore", "Plot 12, Industrial Area"),
        ("Stanley Tools", "Anita Sharma", "anita@stanley.com", "+91-9876543211", "Mumbai", "Andheri East, Industrial Park"),
        ("Asian Paints", "Vijay Patel", "vijay@asianpaints.com", "+91-9876543212", "Ahmedabad", "Sector 7, Paint Hub"),
        ("Havells India", "Priya Singh", "priya@havells.com", "+91-9876543213", "Noida", "Sector 62, Tech Park"),
        ("Supreme Pipes", "Manoj Gupta", "manoj@supreme.com", "+91-9876543214", "Pune", "Hinjewadi Phase 2"),
        ("Anchor Fasteners", "Deepak Joshi", "deepak@anchor.com", "+91-9876543215", "Chennai", "Industrial Estate, Ambattur"),
    ]
    suppliers = []
    for name, contact, email, phone, city, addr in suppliers_data:
        sup = Supplier(name=name, contact_person=contact, email=email, phone=phone, city=city, address=addr)
        suppliers.append(sup)
    db.add_all(suppliers)
    db.flush()

    # --- Products ---
    products_data = [
        ("Bosch Impact Drill 550W", "PWR-001", categories[0].id, suppliers[0].id, 2800, 3499, 25, 5, "A1-01", "piece"),
        ("Bosch Angle Grinder 4\"", "PWR-002", categories[0].id, suppliers[0].id, 2200, 2899, 18, 5, "A1-02", "piece"),
        ("Bosch Jigsaw 500W", "PWR-003", categories[0].id, suppliers[0].id, 3200, 4199, 12, 3, "A1-03", "piece"),
        ("Stanley Hammer 500g", "HND-001", categories[1].id, suppliers[1].id, 350, 499, 50, 10, "A2-01", "piece"),
        ("Stanley Screwdriver Set 8pc", "HND-002", categories[1].id, suppliers[1].id, 420, 649, 35, 10, "piece", "piece"),
        ("Stanley Tape Measure 5m", "HND-003", categories[1].id, suppliers[1].id, 180, 299, 60, 15, "A2-03", "piece"),
        ("Stanley Pliers Set 3pc", "HND-004", categories[1].id, suppliers[1].id, 550, 799, 28, 8, "A2-04", "piece"),
        ("CPVC Pipe 1\" (per ft)", "PLM-001", categories[2].id, suppliers[4].id, 45, 75, 200, 50, "B1-01", "meter"),
        ("PVC Elbow 1\"", "PLM-002", categories[2].id, suppliers[4].id, 12, 25, 150, 30, "B1-02", "piece"),
        ("Ball Valve 1\" Brass", "PLM-003", categories[2].id, suppliers[4].id, 180, 299, 40, 10, "B1-03", "piece"),
        ("Teflon Tape", "PLM-004", categories[2].id, suppliers[4].id, 15, 30, 100, 20, "B1-04", "piece"),
        ("Havells Wire 1.5mm (per m)", "ELC-001", categories[3].id, suppliers[3].id, 18, 32, 500, 100, "B2-01", "meter"),
        ("Havells MCB 16A", "ELC-002", categories[3].id, suppliers[3].id, 140, 225, 45, 10, "B2-02", "piece"),
        ("Havells Switch Board 6-way", "ELC-003", categories[3].id, suppliers[3].id, 280, 450, 30, 8, "B2-03", "piece"),
        ("LED Bulb 9W (Havells)", "ELC-004", categories[3].id, suppliers[3].id, 65, 120, 80, 20, "B2-04", "piece"),
        ("Asian Paint Emulsion 1L", "PNT-001", categories[4].id, suppliers[2].id, 220, 350, 40, 10, "C1-01", "piece"),
        ("Asian Paint Primer 1L", "PNT-002", categories[4].id, suppliers[2].id, 160, 260, 35, 10, "C1-02", "piece"),
        ("Paint Brush 4\"", "PNT-003", categories[4].id, suppliers[2].id, 45, 85, 50, 10, "C1-03", "piece"),
        ("Paint Roller 9\"", "PNT-004", categories[4].id, suppliers[2].id, 90, 160, 30, 8, "C1-04", "piece"),
        ("Wood Screws #8 (box)", "FST-001", categories[5].id, suppliers[5].id, 85, 150, 100, 20, "C2-01", "box"),
        ("Concrete Anchor 10mm (10pc)", "FST-002", categories[5].id, suppliers[5].id, 60, 110, 80, 15, "C2-02", "box"),
        ("Hex Bolt M10 (10pc)", "FST-003", categories[5].id, suppliers[5].id, 45, 85, 70, 15, "C2-03", "box"),
        ("Safety Goggles", "SFT-001", categories[6].id, suppliers[1].id, 120, 199, 30, 8, "D1-01", "piece"),
        ("Work Gloves (pair)", "SFT-002", categories[6].id, suppliers[1].id, 80, 149, 45, 10, "D1-02", "piece"),
        ("Dust Mask N95 (5pc)", "SFT-003", categories[6].id, suppliers[1].id, 150, 250, 40, 10, "D1-03", "box"),
        ("Garden Hose 15m", "GRD-001", categories[7].id, suppliers[4].id, 450, 699, 15, 5, "D2-01", "piece"),
        ("Shovel Heavy Duty", "GRD-002", categories[7].id, suppliers[1].id, 380, 599, 20, 5, "D2-02", "piece"),
        ("White Cement 1kg", "BLD-001", categories[8].id, suppliers[5].id, 35, 60, 100, 25, "E1-01", "kg"),
        ("Wall Putty 5kg", "BLD-002", categories[8].id, suppliers[2].id, 180, 299, 50, 15, "E1-02", "piece"),
        ("Fevicol SH 500g", "ADH-001", categories[9].id, suppliers[5].id, 140, 230, 35, 10, "E2-01", "piece"),
    ]
    products = []
    for name, sku, cat_id, sup_id, cost, sell, qty, min_s, loc, unit in products_data:
        p = Product(
            name=name, sku=sku, category_id=cat_id, supplier_id=sup_id,
            cost_price=cost, selling_price=sell, quantity=qty,
            min_stock=min_s, location=loc, unit=unit
        )
        products.append(p)
    db.add_all(products)
    db.flush()

    # --- Customers ---
    customers_data = [
        ("Ramesh Construction", "ramesh@construction.com", "+91-9800000001", "Sector 15, Noida", "Noida"),
        ("Priya Interiors", "priya@interiors.com", "+91-9800000002", "MG Road, Bangalore", "Bangalore"),
        ("Sharma Electricals", "sharma@electricals.com", "+91-9800000003", "Lajpat Nagar, Delhi", "Delhi"),
        ("Green Gardens Co.", "info@greengardens.com", "+91-9800000004", "Koramangala, Bangalore", "Bangalore"),
        ("Quick Fix Plumbing", "quickfix@plumbing.com", "+91-9800000005", "Andheri, Mumbai", "Mumbai"),
        ("Amit Painters", "amit@painters.com", "+91-9800000006", "Jubilee Hills, Hyderabad", "Hyderabad"),
        ("Walk-in Customer", "", "", "", ""),
    ]
    customers = []
    for name, email, phone, addr, city in customers_data:
        c = Customer(name=name, email=email, phone=phone, address=addr, city=city)
        customers.append(c)
    db.add_all(customers)
    db.flush()

    # --- Sample Sales ---
    base_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    invoice_counter = 1000
    for day_offset in range(30):
        num_sales = random.randint(1, 4)
        for _ in range(num_sales):
            invoice_counter += 1
            sale_date = base_date + datetime.timedelta(days=day_offset, hours=random.randint(9, 18))
            customer = random.choice(customers)
            num_items = random.randint(1, 4)
            sale_items = []
            subtotal = 0

            selected_products = random.sample(products, min(num_items, len(products)))
            for prod in selected_products:
                qty = random.randint(1, 5)
                item_total = qty * prod.selling_price
                subtotal += item_total
                sale_items.append(SaleItem(
                    product_id=prod.id,
                    quantity=qty,
                    unit_price=prod.selling_price,
                    total_price=item_total
                ))

            tax = round(subtotal * 0.18, 2)
            discount = round(subtotal * random.choice([0, 0, 0, 0.05, 0.10]), 2)
            total = round(subtotal + tax - discount, 2)

            sale = Sale(
                invoice_number=f"INV-{invoice_counter}",
                customer_id=customer.id,
                user_id=admin.id,
                subtotal=subtotal,
                tax_amount=tax,
                discount_amount=discount,
                total_amount=total,
                payment_method=random.choice(["cash", "card", "upi"]),
                status="completed",
                created_at=sale_date,
                items=sale_items
            )
            db.add(sale)

    # --- Sample Purchase Orders ---
    po_counter = 500
    for i in range(8):
        po_counter += 1
        supplier = random.choice(suppliers)
        po_date = base_date + datetime.timedelta(days=random.randint(0, 25))
        num_items = random.randint(2, 5)
        po_items = []
        total = 0

        sup_products = [p for p in products if p.supplier_id == supplier.id]
        if not sup_products:
            sup_products = random.sample(products, 3)

        selected = random.sample(sup_products, min(num_items, len(sup_products)))
        for prod in selected:
            qty = random.randint(10, 50)
            cost = qty * prod.cost_price
            total += cost
            po_items.append(PurchaseItem(
                product_id=prod.id,
                quantity=qty,
                unit_cost=prod.cost_price,
                total_cost=cost
            ))

        status = random.choice(["ordered", "received", "received", "received"])
        po = PurchaseOrder(
            po_number=f"PO-{po_counter}",
            supplier_id=supplier.id,
            user_id=admin.id,
            total_amount=total,
            status=status,
            notes=f"Regular stock replenishment",
            expected_date=po_date + datetime.timedelta(days=7),
            received_date=(po_date + datetime.timedelta(days=5)) if status == "received" else None,
            created_at=po_date,
            items=po_items
        )
        db.add(po)

    db.commit()
    print("[OK] Database seeded with sample data!")
