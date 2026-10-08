"""pyui.app - connects State + view function + Renderer + a tiny HTTP server."""
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from .core import Renderer


class App:
    def __init__(self, view, state, title="pyui app"):
        self.view, self.state, self.title = view, state, title
        self.html, self.handlers = "", {}
        state.subscribe(self.rerender)        # state change -> re-render
        self.rerender()

    def rerender(self):
        r = Renderer()
        body = r.render(self.view(self.state))
        self.handlers = r.handlers
        self.html = (f"<!doctype html><html><head><meta charset='utf-8'>"
                     f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
                     f"<title>{self.title}</title></head><body>{body}</body></html>")

    def run(self, host="0.0.0.0", port=None):
        port = port or int(os.environ.get("PORT", 8000))
        app = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                data = app.html.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length).decode()
                fields = {k: v[0] for k, v in parse_qs(raw).items()}
                handler = app.handlers.get(self.path.removeprefix("/_event/"))
                if handler:
                    # handlers may take the form fields or nothing
                    try:
                        handler(fields)
                    except TypeError:
                        handler()
                self.send_response(303)       # redirect so refresh won't resubmit
                self.send_header("Location", "/")
                self.end_headers()

            def log_message(self, *a):
                pass

        print(f"Running on http://localhost:{port}")
        HTTPServer((host, port), Handler).serve_forever()
