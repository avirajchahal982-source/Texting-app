from http.server import HTTPServer, BaseHTTPRequestHandler

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('6.7.6.7', 8080)  # valid IP and port
    httpd = server_class(server_address, handler_class)
    print(f"Serving on http://{server_address[0]}:{server_address[1]}")
    httpd.serve_forever()
