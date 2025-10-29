#!/usr/bin/env python3
"""
CORS Proxy Server voor Open Data APIs

Deze proxy lost het CORS probleem op door requests door te sturen
naar verschillende Open Data APIs en de juiste CORS headers toe te voegen.

Ondersteunt:
- Utrecht Open Data API
- Data.overheid.nl CKAN API
- Woo-analyse functionaliteit
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.error
import json
import sys
from urllib.parse import urlparse, parse_qs

class CORSProxyHandler(SimpleHTTPRequestHandler):
    """HTTP handler die CORS headers toevoegt en API requests proxied."""

    UTRECHT_API_BASE = "https://open.utrecht.nl/api"
    DATAOVERHEID_API_BASE = "https://data.overheid.nl/data/api/3/action"

    def end_headers(self):
        """Voeg CORS headers toe aan alle responses."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        """Handle preflight CORS requests."""
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """Handle GET requests - proxy API calls of serve files."""

        # Als het pad begint met /api/, proxy het naar de Utrecht API
        if self.path.startswith('/api/'):
            self.proxy_api_request()
        # Als het pad begint met /dataoverheid/, proxy naar data.overheid.nl
        elif self.path.startswith('/dataoverheid/'):
            self.proxy_dataoverheid_request()
        # Als het pad begint met /woo/, handle Woo-analyse
        elif self.path.startswith('/woo/analyze/'):
            self.handle_woo_analysis()
        else:
            # Serve static files (HTML, CSS, JS)
            super().do_GET()

    def handle_woo_analysis(self):
        """Handle Woo analysis requests."""
        try:
            # Extract dataset ID from path /woo/analyze/{dataset_id}
            dataset_id = self.path.split('/')[-1]

            # Import WooConnector
            import sys
            import os
            # Add current directory to path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, current_dir)
            from woo_connector import WooConnector

            # Fetch dataset from API
            api_url = f"{self.UTRECHT_API_BASE}/datasets/{dataset_id}"
            req = urllib.request.Request(api_url)
            req.add_header('Accept', 'application/json')

            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
                dataset = data.get('data', data)

            # Run Woo analysis
            connector = WooConnector()
            analysis = connector.analyze_dataset(dataset)

            # Return JSON response
            response_data = json.dumps(analysis, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', len(response_data))
            self.end_headers()
            self.wfile.write(response_data)

        except Exception as e:
            print(f"Woo analysis error: {e}")
            error_response = json.dumps({
                'error': str(e),
                'keywords': [],
                'topics': [],
                'categories': {}
            }).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(error_response))
            self.end_headers()
            self.wfile.write(error_response)

    def proxy_api_request(self):
        """Proxy een request naar de Utrecht Open Data API."""
        try:
            # Bouw de volledige API URL
            api_path = self.path[4:]  # Remove /api prefix
            full_url = f"{self.UTRECHT_API_BASE}{api_path}"

            print(f"Proxying request to: {full_url}")

            # Maak request naar de echte API
            req = urllib.request.Request(full_url)
            req.add_header('Accept', 'application/json')
            req.add_header('User-Agent', 'Utrecht-OpenData-Proxy/1.0')

            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()

                # Stuur response terug naar client met CORS headers
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', len(data))
                self.end_headers()
                self.wfile.write(data)

        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            self.send_error(e.code, f"API Error: {e.reason}")

        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            self.send_error(502, f"Cannot reach API: {e.reason}")

        except Exception as e:
            print(f"Unexpected error: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")

    def proxy_dataoverheid_request(self):
        """Proxy een request naar de data.overheid.nl CKAN API."""
        try:
            # Bouw de volledige API URL
            # Path format: /dataoverheid/{action}?params
            path_parts = self.path[13:]  # Remove /dataoverheid prefix

            # Split action and query params
            if '?' in path_parts:
                action, query = path_parts.split('?', 1)
                full_url = f"{self.DATAOVERHEID_API_BASE}{action}?{query}"
            else:
                full_url = f"{self.DATAOVERHEID_API_BASE}{path_parts}"

            print(f"Proxying request to data.overheid.nl: {full_url}")

            # Maak request naar de CKAN API
            req = urllib.request.Request(full_url)
            req.add_header('Accept', 'application/json')
            req.add_header('User-Agent', 'DataOverheid-Proxy/1.0')

            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()

                # Stuur response terug naar client met CORS headers
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', len(data))
                self.end_headers()
                self.wfile.write(data)

        except urllib.error.HTTPError as e:
            print(f"HTTP Error: {e.code} - {e.reason}")
            self.send_error(e.code, f"API Error: {e.reason}")
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}")
            self.send_error(502, f"Cannot reach data.overheid.nl: {e.reason}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")

    def log_message(self, format, *args):
        """Custom logging."""
        sys.stdout.write("%s - - [%s] %s\n" %
                        (self.address_string(),
                         self.log_date_time_string(),
                         format % args))


def run_server(port=8080):
    """Start de proxy server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSProxyHandler)

    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  Utrecht Open Data CORS Proxy Server                         ║
╚═══════════════════════════════════════════════════════════════╝

✓ Server draait op: http://localhost:{port}
✓ API proxy endpoint: http://localhost:{port}/api/datasets
✓ CORS headers worden automatisch toegevoegd

Open je browser op: http://localhost:{port}

Druk op Ctrl+C om te stoppen.
""")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer gestopt.")
        httpd.server_close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Utrecht Open Data CORS Proxy')
    parser.add_argument('-p', '--port', type=int, default=8080,
                       help='Poort waarop de server draait (standaard: 8080)')

    args = parser.parse_args()
    run_server(args.port)
