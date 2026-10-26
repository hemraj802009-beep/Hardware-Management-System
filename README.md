# Sharma Hardware Store Website

A modern, clean, organized hardware store website and management platform with an MVC-style architecture.

---

## 📁 Project Directory Structure

```text
hardware store website/
├── app.py                      # Main application entry point to start the server
├── sharmahardware.py           # Alternate entry point (for backward compatibility)
├── controllers/                # Backend Controllers & Business Logic
│   ├── __init__.py             # Package init
│   ├── store_controller.py     # Product data, categories, inventory stats & template loaders
│   └── server_controller.py    # HTTP Request dispatcher, clean routing, static file & API handling
├── templates/                  # HTML Views & Storefront Templates
│   ├── index.html              # Main landing page
│   ├── sharma_premium.html     # Premium storefront showcase
│   ├── sharma_pro.html         # Full products catalog & shop view
│   ├── sharmahardware.html     # Store physical location & Google Maps embed
│   ├── sharma_cart.html        # Shopping cart view
│   ├── sharma_checkout.html    # Customer order checkout
│   ├── sharma_order_success.html # Order confirmation
│   ├── sharma_product_detail.html # Product detail view
│   ├── sharma_dashboard.html   # Inventory & business management dashboard
│   ├── cement_steel.html       # Cement & Steel category
│   ├── plumbing.html           # Pipes & Plumbing category
│   ├── tools.html              # Power & Hand Tools category
│   ├── electrical.html         # Electrical & Wires category
│   ├── paints.html             # Paints & Waterproofing category
│   └── sanitary.html           # Sanitaryware category
├── images/                     # Product & Background Images
│   ├── hardware_bg_1.jpg       # Hero hardware background
│   ├── hardware_bg_2.jpg       # Store texture background
│   ├── prod_1.jpg to prod_8.jpg # Product catalog photos
└── scripts/                    # Utility & Maintenance Scripts
    ├── fix_all.py, link_cat.py, make_cats.py, etc.
```

---

## 🚀 How to Run the Project

Run either command from the project root:

```bash
python app.py
```
*or*
```bash
python sharmahardware.py
```

The server will automatically start at:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🌐 Clean Routes & Endpoints

| URL Route | Template / Response | Description |
| :--- | :--- | :--- |
| `/` or `/home` | `templates/index.html` | Storefront Homepage |
| `/catalog` or `/products` | `templates/sharma_pro.html` | Full product catalog & filter |
| `/cart` | `templates/sharma_cart.html` | Shopping Cart |
| `/checkout` | `templates/sharma_checkout.html` | Checkout and delivery form |
| `/success` | `templates/sharma_order_success.html` | Order confirmed screen |
| `/store` | `templates/sharmahardware.html` | Location in Ner Chowk & Map |
| `/dashboard` | `templates/sharma_dashboard.html` | Stock & inventory admin panel |
| `/api/products` | JSON | Product catalog REST API |
| `/api/categories` | JSON | Categories REST API |
| `/api/stats` | JSON | Inventory statistics REST API |
| `/images/<filename>` | `images/<filename>` | Static product images & assets |
