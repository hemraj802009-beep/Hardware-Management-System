from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models import User, Category, Supplier, Product
from auth import hash_password

TEST_DB_URL = "sqlite:///./test_debug.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=test_engine)
db = TestSessionLocal()

admin = User(username="admin", email="admin@test.com", hashed_password=hash_password("admin123"), full_name="Test Admin", role="admin")
db.add(admin)
db.flush()
cat = Category(name="Power Tools", description="Electric tools", icon="fas fa-bolt")
db.add(cat)
db.flush()
supplier = Supplier(name="Test Supplier", contact_person="John", email="john@test.com", phone="1234567890", city="TestCity")
db.add(supplier)
db.flush()
product = Product(name="Test Drill", sku="TST-001", category_id=cat.id, supplier_id=supplier.id, cost_price=100, selling_price=150, quantity=50, min_stock=5, location="A1", unit="piece")
db.add(product)
db.commit()
db.close()

client = TestClient(app)
resp = client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=False)
client.cookies = resp.cookies
auth_client = client

resp = auth_client.post("/sales/pos/checkout", json={"items": [{"product_id": 1, "quantity": 3}], "payment_method": "cash", "discount": 0})
print(resp.json())
sale_id = resp.json()["sale_id"]
db = TestSessionLocal()
p = db.query(Product).filter(Product.id == 1).first()
stock_after_sale = p.quantity
print('after sale:', stock_after_sale)
db.close()
auth_client.get(f"/sales/cancel/{sale_id}", follow_redirects=False)
db = TestSessionLocal()
p = db.query(Product).filter(Product.id == 1).first()
print('after cancel:', p.quantity)
db.close()
