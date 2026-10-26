"""
Store Controller for Sharma Hardware Store.
Manages product data, category definitions, inventory statistics, and template loading.
"""

from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
IMAGES_DIR = BASE_DIR / "images"


class StoreController:
    """Handles business logic for the hardware store website."""

    CATEGORIES = [
        {
            "id": "cement-steel",
            "name": "Cement, TMT & Structural Steel",
            "template": "cement_steel.html",
            "image": "images/prod_1.jpg",
            "description": "OPC Cement, PPC Cement, TMT Bars, MS Angles, Channels & more",
        },
        {
            "id": "plumbing",
            "name": "Pipes, Fittings & Plumbing",
            "template": "plumbing.html",
            "image": "images/prod_4.jpg",
            "description": "UPVC, CPVC pipes, brass fittings, ball valves and water storage",
        },
        {
            "id": "tools",
            "name": "Power Tools & Hand Tools",
            "template": "tools.html",
            "image": "images/prod_3.jpg",
            "description": "Drills, angle grinders, circular saws, wrenches, hammers & kits",
        },
        {
            "id": "electrical",
            "name": "Electrical, Switches & Wires",
            "template": "electrical.html",
            "image": "images/prod_5.jpg",
            "description": "Copper wires, modular switches, MCBs, distribution boards & LEDs",
        },
        {
            "id": "paints",
            "name": "Paints, Putty & Waterproofing",
            "template": "paints.html",
            "image": "images/prod_6.jpg",
            "description": "Exterior & interior emulsions, wall putty, primer & waterproofing chemicals",
        },
        {
            "id": "sanitary",
            "name": "Sanitaryware & Bath Fittings",
            "template": "sanitary.html",
            "image": "images/prod_7.jpg",
            "description": "Wash basins, commodes, stainless steel sinks, showers and bib cocks",
        },
    ]

    PRODUCTS = [
        {
            "id": 1,
            "name": "Ultratech OPC 43 Grade Cement",
            "category": "Cement & Steel",
            "unit": "50kg Bag",
            "price": 390,
            "image": "images/prod_1.jpg",
            "badge": "Best Seller",
            "in_stock": True,
            "description": "High quality OPC 43 grade cement suitable for residential and commercial construction.",
        },
        {
            "id": 2,
            "name": "Fe 500D TMT Rebars",
            "category": "Cement & Steel",
            "unit": "Per Kg",
            "price": 76,
            "image": "images/prod_2.jpg",
            "badge": "Popular",
            "in_stock": True,
            "description": "High ductility earthquake-resistant Fe 500D primary steel rebars.",
        },
        {
            "id": 3,
            "name": "Professional 850W Angle Grinder",
            "category": "Power Tools",
            "unit": "Piece",
            "price": 1899,
            "image": "images/prod_3.jpg",
            "badge": "Top Rated",
            "in_stock": True,
            "description": "Heavy-duty electric angle grinder with guard and spindle lock for metal and stone cutting.",
        },
        {
            "id": 4,
            "name": "UPVC Heavy Duty Plumbing Pipes",
            "category": "Plumbing",
            "unit": "6m Length",
            "price": 420,
            "image": "images/prod_4.jpg",
            "badge": "Essential",
            "in_stock": True,
            "description": "Lead-free, UV resistant UPVC plumbing pipe for reliable household water distribution.",
        },
        {
            "id": 5,
            "name": "Flame Retardant House Wire (1.5 sq mm)",
            "category": "Electrical",
            "unit": "90m Coil",
            "price": 1450,
            "image": "images/prod_5.jpg",
            "badge": "Certified",
            "in_stock": True,
            "description": "100% pure electrolytic grade copper wire with flame retardant PVC insulation.",
        },
        {
            "id": 6,
            "name": "WeatherShield Exterior Emulsion",
            "category": "Paints",
            "unit": "20L Drum",
            "price": 4850,
            "image": "images/prod_6.jpg",
            "badge": "Premium",
            "in_stock": True,
            "description": "Advanced silicone-modified acrylic exterior emulsion for extreme weather resistance.",
        },
        {
            "id": 7,
            "name": "Brass Ceramic Disc Bib Cock Faucet",
            "category": "Sanitaryware",
            "unit": "Piece",
            "price": 680,
            "image": "images/prod_7.jpg",
            "badge": "Durable",
            "in_stock": True,
            "description": "Solid forged brass bathroom bib cock with mirror chrome finish and drip-free ceramic cartridge.",
        },
        {
            "id": 8,
            "name": "Impact Drill 650W with 13mm Chuck",
            "category": "Power Tools",
            "unit": "Kit",
            "price": 2490,
            "image": "images/prod_8.jpg",
            "badge": "Pro Choice",
            "in_stock": True,
            "description": "Variable speed reversible impact drill with auxiliary handle and depth gauge.",
        },
    ]

    @classmethod
    def get_categories(cls):
        """Returns the list of product categories."""
        return cls.CATEGORIES

    @classmethod
    def get_products(cls):
        """Returns the full product catalog."""
        return cls.PRODUCTS

    @classmethod
    def get_product_by_id(cls, product_id):
        """Finds a single product by ID."""
        for p in cls.PRODUCTS:
            if p["id"] == product_id:
                return p
        return None

    @classmethod
    def get_dashboard_stats(cls):
        """Returns summarized metrics for the inventory dashboard."""
        return {
            "total_items_in_stock": 5420,
            "categories_count": len(cls.CATEGORIES),
            "pending_orders": 8,
            "monthly_turnover": "Rs. 18.4 Lakhs",
            "critical_stock_alerts": 2,
        }

    @classmethod
    def get_template_path(cls, template_name: str) -> Path | None:
        """Resolves template file path within the templates directory."""
        if not template_name.endswith(".html"):
            template_name = f"{template_name}.html"
        
        target = (TEMPLATES_DIR / template_name).resolve()
        # Security check: ensure target stays inside TEMPLATES_DIR
        if str(target).startswith(str(TEMPLATES_DIR.resolve())) and target.is_file():
            return target
        return None

    @classmethod
    def render_template(cls, template_name: str) -> tuple[bytes, str]:
        """
        Loads and returns the template content and MIME type.
        Returns (content_bytes, 'text/html; charset=utf-8').
        """
        path = cls.get_template_path(template_name)
        if path and path.is_file():
            return path.read_bytes(), "text/html; charset=utf-8"
        return b"<h1>404 - Template Not Found</h1>", "text/html; charset=utf-8"
