"""Comprehensive tests for Hardware Store Management System."""
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Base, get_db
from main import app
from models import User, Category, Supplier, Product, Customer, Sale, SaleItem, PurchaseOrder
from auth import hash_password

# Test database setup
TEST_DB_URL = "sqlite:///./test_hardware_store.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()

    # Seed minimal test data
    admin = User(
        username="admin", email="admin@test.com",
        hashed_password=hash_password("admin123"),
        full_name="Test Admin", role="admin"
    )
    db.add(admin)
    db.flush()

    cat = Category(name="Power Tools", description="Electric tools", icon="fas fa-bolt")
    db.add(cat)
    db.flush()

    supplier = Supplier(name="Test Supplier", contact_person="John", email="john@test.com", phone="1234567890", city="TestCity")
    db.add(supplier)
    db.flush()

    product = Product(
        name="Test Drill", sku="TST-001", category_id=cat.id,
        supplier_id=supplier.id, cost_price=100, selling_price=150,
        quantity=50, min_stock=5, location="A1", unit="piece"
    )
    product2 = Product(
        name="Test Hammer", sku="TST-002", category_id=cat.id,
        supplier_id=supplier.id, cost_price=50, selling_price=80,
        quantity=3, min_stock=5, location="A2", unit="piece"
    )
    db.add_all([product, product2])
    db.flush()

    customer = Customer(name="Test Customer", email="cust@test.com", phone="9876543210", city="TestCity")
    db.add(customer)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def auth_client(client):
    """Create an authenticated test client."""
    resp = client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=False)
    assert resp.status_code == 302
    cookies = resp.cookies
    client.cookies = cookies
    return client


# ===================================
# AUTH TESTS
# ===================================
class TestAuth:
    def test_login_page_renders(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert "HardwareHub" in resp.text
        assert "Sign in" in resp.text

    def test_login_success(self, client):
        resp = client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == "/"
        assert "access_token" in resp.cookies

    def test_login_wrong_password(self, client):
        resp = client.post("/login", data={"username": "admin", "password": "wrong"})
        assert resp.status_code == 200
        assert "Invalid username or password" in resp.text

    def test_login_wrong_username(self, client):
        resp = client.post("/login", data={"username": "nobody", "password": "admin123"})
        assert resp.status_code == 200
        assert "Invalid username or password" in resp.text

    def test_logout(self, auth_client):
        resp = auth_client.get("/logout", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == "/login"

    def test_unauthenticated_redirect(self, client):
        resp = client.get("/", follow_redirects=False)
        assert resp.status_code == 302
        assert "/login" in resp.headers["location"]

    def test_login_page_redirect_when_logged_in(self, auth_client):
        resp = auth_client.get("/login", follow_redirects=False)
        assert resp.status_code == 302
        assert resp.headers["location"] == "/"


# ===================================
# DASHBOARD TESTS
# ===================================
class TestDashboard:
    def test_dashboard_renders(self, auth_client):
        resp = auth_client.get("/")
        assert resp.status_code == 200
        assert "Dashboard" in resp.text

    def test_dashboard_shows_metrics(self, auth_client):
        resp = auth_client.get("/")
        assert "Today" in resp.text
        assert "Products" in resp.text
        assert "Customers" in resp.text

    def test_dashboard_has_charts(self, auth_client):
        resp = auth_client.get("/")
        assert "salesChart" in resp.text
        assert "categoryChart" in resp.text


# ===================================
# PRODUCT TESTS
# ===================================
class TestProducts:
    def test_list_products(self, auth_client):
        resp = auth_client.get("/products")
        assert resp.status_code == 200
        assert "Test Drill" in resp.text
        assert "TST-001" in resp.text

    def test_add_product_page(self, auth_client):
        resp = auth_client.get("/products/add")
        assert resp.status_code == 200
        assert "Add New Product" in resp.text

    def test_add_product(self, auth_client):
        resp = auth_client.post("/products/add", data={
            "name": "New Product",
            "sku": "NEW-001",
            "description": "A new test product",
            "category_id": 1,
            "supplier_id": 1,
            "cost_price": 200,
            "selling_price": 300,
            "quantity": 25,
            "min_stock": 5,
            "location": "B1",
            "unit": "piece",
        }, follow_redirects=False)
        assert resp.status_code == 302

        # Verify it appears in list
        resp = auth_client.get("/products")
        assert "New Product" in resp.text
        assert "NEW-001" in resp.text

    def test_add_duplicate_sku(self, auth_client):
        resp = auth_client.post("/products/add", data={
            "name": "Duplicate", "sku": "TST-001",
            "cost_price": 100, "selling_price": 150,
            "quantity": 10, "min_stock": 5, "unit": "piece",
        })
        assert resp.status_code == 200
        assert "already exists" in resp.text

    def test_edit_product_page(self, auth_client):
        resp = auth_client.get("/products/edit/1")
        assert resp.status_code == 200
        assert "Edit Product" in resp.text
        assert "Test Drill" in resp.text

    def test_edit_product(self, auth_client):
        resp = auth_client.post("/products/edit/1", data={
            "name": "Updated Drill", "sku": "TST-001",
            "description": "", "category_id": 1, "supplier_id": 1,
            "cost_price": 120, "selling_price": 180,
            "quantity": 45, "min_stock": 5,
            "location": "A1", "unit": "piece",
        }, follow_redirects=False)
        assert resp.status_code == 302

        resp = auth_client.get("/products")
        assert "Updated Drill" in resp.text

    def test_delete_product(self, auth_client):
        resp = auth_client.get("/products/delete/1", follow_redirects=False)
        assert resp.status_code == 302

    def test_search_products(self, auth_client):
        resp = auth_client.get("/products?q=Drill")
        assert resp.status_code == 200
        assert "Test Drill" in resp.text

    def test_filter_low_stock(self, auth_client):
        resp = auth_client.get("/products?stock=low")
        assert resp.status_code == 200
        assert "Test Hammer" in resp.text

    def test_filter_by_category(self, auth_client):
        resp = auth_client.get("/products?cat=1")
        assert resp.status_code == 200

    def test_edit_nonexistent_product(self, auth_client):
        resp = auth_client.get("/products/edit/9999", follow_redirects=False)
        assert resp.status_code == 302


# ===================================
# CATEGORY TESTS
# ===================================
class TestCategories:
    def test_list_categories(self, auth_client):
        resp = auth_client.get("/categories")
        assert resp.status_code == 200
        assert "Power Tools" in resp.text

    def test_add_category(self, auth_client):
        resp = auth_client.post("/categories/add", data={
            "name": "Hand Tools", "description": "Manual tools", "icon": "fas fa-wrench"
        }, follow_redirects=False)
        assert resp.status_code == 302

        resp = auth_client.get("/categories")
        assert "Hand Tools" in resp.text

    def test_add_duplicate_category(self, auth_client):
        resp = auth_client.post("/categories/add", data={
            "name": "Power Tools", "description": "Duplicate", "icon": "fas fa-bolt"
        }, follow_redirects=False)
        assert resp.status_code == 302

    def test_edit_category(self, auth_client):
        resp = auth_client.post("/categories/edit/1", data={
            "name": "Electric Tools", "description": "Updated", "icon": "fas fa-bolt"
        }, follow_redirects=False)
        assert resp.status_code == 302

    def test_delete_category_with_products(self, auth_client):
        """Should not delete category that has products."""
        resp = auth_client.get("/categories/delete/1", follow_redirects=False)
        assert resp.status_code == 302
        # Category should still exist
        resp = auth_client.get("/categories")
        assert "Power Tools" in resp.text


# ===================================
# SUPPLIER TESTS
# ===================================
class TestSuppliers:
    def test_list_suppliers(self, auth_client):
        resp = auth_client.get("/suppliers")
        assert resp.status_code == 200
        assert "Test Supplier" in resp.text

    def test_add_supplier_page(self, auth_client):
        resp = auth_client.get("/suppliers/add")
        assert resp.status_code == 200
        assert "Add Supplier" in resp.text

    def test_add_supplier(self, auth_client):
        resp = auth_client.post("/suppliers/add", data={
            "name": "New Supplier", "contact_person": "Jane",
            "email": "jane@new.com", "phone": "1111111111",
            "address": "123 Street", "city": "NewCity"
        }, follow_redirects=False)
        assert resp.status_code == 302

        resp = auth_client.get("/suppliers")
        assert "New Supplier" in resp.text

    def test_edit_supplier(self, auth_client):
        resp = auth_client.get("/suppliers/edit/1")
        assert resp.status_code == 200
        assert "Test Supplier" in resp.text

        resp = auth_client.post("/suppliers/edit/1", data={
            "name": "Updated Supplier", "contact_person": "John Updated",
            "email": "john@updated.com", "phone": "1234567890",
            "address": "", "city": "UpdatedCity"
        }, follow_redirects=False)
        assert resp.status_code == 302

    def test_delete_supplier(self, auth_client):
        resp = auth_client.get("/suppliers/delete/1", follow_redirects=False)
        assert resp.status_code == 302

    def test_search_suppliers(self, auth_client):
        resp = auth_client.get("/suppliers?q=Test")
        assert resp.status_code == 200
        assert "Test Supplier" in resp.text

    def test_edit_nonexistent_supplier(self, auth_client):
        resp = auth_client.get("/suppliers/edit/9999", follow_redirects=False)
        assert resp.status_code == 302


# ===================================
# CUSTOMER TESTS
# ===================================
class TestCustomers:
    def test_list_customers(self, auth_client):
        resp = auth_client.get("/customers")
        assert resp.status_code == 200
        assert "Test Customer" in resp.text

    def test_add_customer_page(self, auth_client):
        resp = auth_client.get("/customers/add")
        assert resp.status_code == 200
        assert "Add Customer" in resp.text

    def test_add_customer(self, auth_client):
        resp = auth_client.post("/customers/add", data={
            "name": "New Customer", "email": "new@cust.com",
            "phone": "5555555555", "address": "456 Ave", "city": "CustCity"
        }, follow_redirects=False)
        assert resp.status_code == 302

        resp = auth_client.get("/customers")
        assert "New Customer" in resp.text

    def test_edit_customer(self, auth_client):
        resp = auth_client.get("/customers/edit/1")
        assert resp.status_code == 200

        resp = auth_client.post("/customers/edit/1", data={
            "name": "Updated Customer", "email": "up@cust.com",
            "phone": "9876543210", "address": "", "city": "UpCity"
        }, follow_redirects=False)
        assert resp.status_code == 302

    def test_delete_customer(self, auth_client):
        resp = auth_client.get("/customers/delete/1", follow_redirects=False)
        assert resp.status_code == 302

    def test_search_customers(self, auth_client):
        resp = auth_client.get("/customers?q=Test")
        assert resp.status_code == 200


# ===================================
# SALES TESTS
# ===================================
class TestSales:
    def test_sales_list(self, auth_client):
        resp = auth_client.get("/sales")
        assert resp.status_code == 200
        assert "Sales" in resp.text

    def test_pos_page(self, auth_client):
        resp = auth_client.get("/sales/pos")
        assert resp.status_code == 200
        assert "Point of Sale" in resp.text
        assert "Test Drill" in resp.text

    def test_pos_checkout_success(self, auth_client):
        resp = auth_client.post("/sales/pos/checkout", json={
            "items": [{"product_id": 1, "quantity": 2}],
            "customer_id": 1,
            "payment_method": "cash",
            "discount": 0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "INV-" in data["invoice_number"]
        assert data["total"] > 0

    def test_pos_checkout_empty_cart(self, auth_client):
        resp = auth_client.post("/sales/pos/checkout", json={
            "items": [],
            "payment_method": "cash",
            "discount": 0,
        })
        assert resp.status_code == 400
        assert resp.json()["error"] == "No items in cart"

    def test_pos_checkout_insufficient_stock(self, auth_client):
        resp = auth_client.post("/sales/pos/checkout", json={
            "items": [{"product_id": 1, "quantity": 999}],
            "payment_method": "cash",
            "discount": 0,
        })
        assert resp.status_code == 400
        assert "Insufficient stock" in resp.json()["error"]

    def test_pos_checkout_invalid_product(self, auth_client):
        resp = auth_client.post("/sales/pos/checkout", json={
            "items": [{"product_id": 9999, "quantity": 1}],
            "payment_method": "cash",
            "discount": 0,
        })
        assert resp.status_code == 400

    def test_pos_checkout_with_discount(self, auth_client):
        resp = auth_client.post("/sales/pos/checkout", json={
            "items": [{"product_id": 1, "quantity": 1}],
            "payment_method": "upi",
            "discount": 10,
        })
        data = resp.json()
        assert data["success"] is True
        # Total should be less due to discount
        expected_subtotal = 150
        expected_tax = expected_subtotal * 0.18
        expected_discount = expected_subtotal * 0.10
        expected_total = round(expected_subtotal + expected_tax - expected_discount, 2)
        assert data["total"] == expected_total

    def test_pos_reduces_stock(self, auth_client):
        # Product 1 starts with qty 50
        auth_client.post("/sales/pos/checkout", json={
            "items": [{"product_id": 1, "quantity": 5}],
            "payment_method": "cash",
            "discount": 0,
        })
        # Check product stock was reduced
        db = TestSessionLocal()
        product = db.query(Product).filter(Product.id == 1).first()
        assert product.quantity == 45
        db.close()

    def test_view_sale_invoice(self, auth_client):
        # Create a sale first
        resp = auth_client.post("/sales/pos/checkout", json={
            "items": [{"product_id": 1, "quantity": 1}],
            "payment_method": "cash",
            "discount": 0,
        })
        sale_id = resp.json()["sale_id"]

        resp = auth_client.get(f"/sales/view/{sale_id}")
        assert resp.status_code == 200
        assert "INVOICE" in resp.text

    def test_cancel_sale_restores_stock(self, auth_client):
        # Create a sale
        resp = auth_client.post("/sales/pos/checkout", json={
            "items": [{"product_id": 1, "quantity": 3}],
            "payment_method": "cash",
            "discount": 0,
        })
        sale_id = resp.json()["sale_id"]

        db = TestSessionLocal()
        p = db.query(Product).filter(Product.id == 1).first()
        stock_after_sale = p.quantity
        db.close()

        # Cancel
        auth_client.get(f"/sales/cancel/{sale_id}", follow_redirects=False)

        db = TestSessionLocal()
        p = db.query(Product).filter(Product.id == 1).first()
        assert p.quantity == stock_after_sale + 3
        db.close()

    def test_sales_filter_by_status(self, auth_client):
        resp = auth_client.get("/sales?status=completed")
        assert resp.status_code == 200

    def test_sales_search(self, auth_client):
        resp = auth_client.get("/sales?q=INV-")
        assert resp.status_code == 200

    def test_api_search_products(self, auth_client):
        resp = auth_client.get("/sales/api/products?q=Drill")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["name"] == "Test Drill"

    def test_view_nonexistent_sale(self, auth_client):
        resp = auth_client.get("/sales/view/9999", follow_redirects=False)
        assert resp.status_code == 302


# ===================================
# PURCHASE ORDER TESTS
# ===================================
class TestPurchases:
    def test_list_purchases(self, auth_client):
        resp = auth_client.get("/purchases")
        assert resp.status_code == 200
        assert "Purchase Orders" in resp.text

    def test_add_purchase_page(self, auth_client):
        resp = auth_client.get("/purchases/add")
        assert resp.status_code == 200
        assert "Create Purchase Order" in resp.text

    def test_create_purchase_order(self, auth_client):
        resp = auth_client.post("/purchases/add", data={
            "supplier_id": "1",
            "notes": "Test PO",
            "expected_date": "2026-11-01",
            "items[0][product_id]": "1",
            "items[0][quantity]": "20",
            "items[0][unit_cost]": "100",
        }, follow_redirects=False)
        assert resp.status_code == 302

        resp = auth_client.get("/purchases")
        assert "PO-" in resp.text

    def test_receive_purchase_order(self, auth_client):
        # Create PO
        auth_client.post("/purchases/add", data={
            "supplier_id": "1",
            "notes": "To receive",
            "expected_date": "",
            "items[0][product_id]": "1",
            "items[0][quantity]": "10",
            "items[0][unit_cost]": "100",
        }, follow_redirects=False)

        db = TestSessionLocal()
        po = db.query(PurchaseOrder).first()
        po_id = po.id
        p_before = db.query(Product).filter(Product.id == 1).first()
        stock_before = p_before.quantity
        db.close()

        # Receive
        resp = auth_client.get(f"/purchases/receive/{po_id}", follow_redirects=False)
        assert resp.status_code == 302

        db = TestSessionLocal()
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        assert po.status == "received"
        p = db.query(Product).filter(Product.id == 1).first()
        assert p.quantity == stock_before + 10
        db.close()

    def test_cancel_purchase_order(self, auth_client):
        auth_client.post("/purchases/add", data={
            "supplier_id": "1",
            "notes": "",
            "expected_date": "",
            "items[0][product_id]": "1",
            "items[0][quantity]": "5",
            "items[0][unit_cost]": "100",
        }, follow_redirects=False)

        db = TestSessionLocal()
        po = db.query(PurchaseOrder).first()
        po_id = po.id
        db.close()

        resp = auth_client.get(f"/purchases/cancel/{po_id}", follow_redirects=False)
        assert resp.status_code == 302

        db = TestSessionLocal()
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
        assert po.status == "cancelled"
        db.close()

    def test_view_purchase(self, auth_client):
        auth_client.post("/purchases/add", data={
            "supplier_id": "1",
            "notes": "View test",
            "expected_date": "",
            "items[0][product_id]": "1",
            "items[0][quantity]": "5",
            "items[0][unit_cost]": "100",
        }, follow_redirects=False)

        db = TestSessionLocal()
        po = db.query(PurchaseOrder).first()
        po_id = po.id
        db.close()

        resp = auth_client.get(f"/purchases/view/{po_id}")
        assert resp.status_code == 200
        assert "Purchase Order" in resp.text

    def test_filter_by_status(self, auth_client):
        resp = auth_client.get("/purchases?status=ordered")
        assert resp.status_code == 200


# ===================================
# REPORT TESTS
# ===================================
class TestReports:
    def test_sales_report(self, auth_client):
        resp = auth_client.get("/reports?type=sales&period=30")
        assert resp.status_code == 200
        assert "Total Revenue" in resp.text

    def test_products_report(self, auth_client):
        resp = auth_client.get("/reports?type=products&period=30")
        assert resp.status_code == 200
        assert "Top Selling" in resp.text

    def test_inventory_report(self, auth_client):
        resp = auth_client.get("/reports?type=inventory&period=30")
        assert resp.status_code == 200
        assert "Total Items" in resp.text

    def test_customer_report(self, auth_client):
        resp = auth_client.get("/reports?type=customers&period=30")
        assert resp.status_code == 200
        assert "Top Customers" in resp.text

    def test_report_period_7_days(self, auth_client):
        resp = auth_client.get("/reports?type=sales&period=7")
        assert resp.status_code == 200

    def test_report_period_90_days(self, auth_client):
        resp = auth_client.get("/reports?type=sales&period=90")
        assert resp.status_code == 200


# ===================================
# AUTH GUARD TESTS
# ===================================
class TestAuthGuards:
    """Verify all routes redirect when not logged in."""

    @pytest.mark.parametrize("url", [
        "/", "/products", "/products/add", "/products/edit/1",
        "/categories", "/suppliers", "/suppliers/add",
        "/customers", "/customers/add",
        "/sales", "/sales/pos",
        "/purchases", "/purchases/add",
        "/reports",
    ])
    def test_unauthenticated_redirects(self, client, url):
        resp = client.get(url, follow_redirects=False)
        assert resp.status_code == 302 or resp.status_code == 307
