"""
Server Controller for Sharma Hardware Store.
Inherits from SimpleHTTPRequestHandler to cleanly map routes, templates, images, and JSON APIs.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import json
import os

from .store_controller import StoreController, BASE_DIR, TEMPLATES_DIR, IMAGES_DIR

HOST = "127.0.0.1"
PORT = 8000

# Route mappings for clean URLs -> templates
ROUTE_MAP = {
    "/": "index.html",
    "/home": "index.html",
    "/index": "index.html",
    "/index.html": "index.html",
    "/premium": "sharma_premium.html",
    "/sharma_premium.html": "sharma_premium.html",
    "/catalog": "sharma_pro.html",
    "/products": "sharma_pro.html",
    "/shop": "sharma_pro.html",
    "/sharma_pro.html": "sharma_pro.html",
    "/store": "sharmahardware.html",
    "/sharmahardware.html": "sharmahardware.html",
    "/info": "sharma_hardware.html",
    "/sharma_hardware.html": "sharma_hardware.html",
    "/cart": "sharma_cart.html",
    "/sharma_cart.html": "sharma_cart.html",
    "/checkout": "sharma_checkout.html",
    "/sharma_checkout.html": "sharma_checkout.html",
    "/success": "sharma_order_success.html",
    "/sharma_order_success.html": "sharma_order_success.html",
    "/product-detail": "sharma_product_detail.html",
    "/sharma_product_detail.html": "sharma_product_detail.html",
    "/dashboard": "sharma_dashboard.html",
    "/sharma_dashboard.html": "sharma_dashboard.html",
    "/cement-steel": "cement_steel.html",
    "/cement_steel.html": "cement_steel.html",
    "/plumbing": "plumbing.html",
    "/plumbing.html": "plumbing.html",
    "/tools": "tools.html",
    "/tools.html": "tools.html",
    "/electrical": "electrical.html",
    "/electrical.html": "electrical.html",
    "/paints": "paints.html",
    "/paints.html": "paints.html",
    "/sanitary": "sanitary.html",
    "/sanitary.html": "sanitary.html",
    "/sohanlal": "sohanlal.html",
    "/sohanlal.html": "sohanlal.html",
    "/sohanlal_dashboard.html": "sohanlal_dashboard.html",
}


class StoreRequestHandler(SimpleHTTPRequestHandler):
    """Handles static files, templates, and API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        if not path:
            path = "/"

        # API Routes
        if path == "/api/products":
            return self._send_json(StoreController.get_products())
        if path == "/api/categories":
            return self._send_json(StoreController.get_categories())
        if path == "/api/stats":
            return self._send_json(StoreController.get_dashboard_stats())

        return super().do_GET()

    def translate_path(self, path):
        """Map URL paths to template files or image files in their respective folders."""
        parsed = urlparse(path)
        clean_path = parsed.path.rstrip("/")
        if not clean_path:
            clean_path = "/"

        # 1. Check clean route map
        if clean_path in ROUTE_MAP:
            target_tmpl = TEMPLATES_DIR / ROUTE_MAP[clean_path]
            if target_tmpl.is_file():
                return str(target_tmpl)

        # 2. Check /images/... request
        if clean_path.startswith("/images/"):
            img_rel = clean_path[len("/images/"):]
            target_img = (IMAGES_DIR / img_rel).resolve()
            if target_img.is_file() and str(target_img).startswith(str(IMAGES_DIR.resolve())):
                return str(target_img)

        # 3. Fallback for root-level image requests (e.g. /prod_1.jpg)
        filename = Path(clean_path).name
        if filename and filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".svg")):
            target_img = (IMAGES_DIR / filename).resolve()
            if target_img.is_file():
                return str(target_img)

        # 4. Check if request matches any template in templates/
        tmpl_file = (TEMPLATES_DIR / filename).resolve()
        if tmpl_file.is_file():
            return str(tmpl_file)
        
        tmpl_with_ext = (TEMPLATES_DIR / f"{filename}.html").resolve()
        if tmpl_with_ext.is_file():
            return str(tmpl_with_ext)

        # Fallback to standard base dir resolution
        return super().translate_path(path)

    def _send_json(self, data):
        content = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def run_server(host=HOST, port=PORT):
    """Starts the HTTP server with multi-port fallback."""
    for p in (port, 8080, 8081, 8082):
        try:
            server = ThreadingHTTPServer((host, p), StoreRequestHandler)
            print("=" * 65)
            print(f"  SHARMA HARDWARE STORE - RUNNING WITH MVC STRUCTURE")
            print(f"  URL: http://{host}:{p}/")
            print("=" * 65)
            print("  Folders:")
            print("   • Templates:   ./templates/")
            print("   • Images:      ./images/")
            print("   • Controllers: ./controllers/")
            print("   • Scripts:     ./scripts/")
            print("-" * 65)
            print("  Key Routes:")
            print(f"   • Home Page:        http://{host}:{p}/")
            print(f"   • Catalog:          http://{host}:{p}/catalog")
            print(f"   • Cart:             http://{host}:{p}/cart")
            print(f"   • Checkout:         http://{host}:{p}/checkout")
            print(f"   • Store Info & Map: http://{host}:{p}/store")
            print(f"   • Dashboard:        http://{host}:{p}/dashboard")
            print(f"   • Products API:     http://{host}:{p}/api/products")
            print("=" * 65)
            print("Press Ctrl+C to stop the server.\n")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")
            finally:
                server.server_close()
            return
        except OSError:
            if p == 8082:
                raise
            continue
