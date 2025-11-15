def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ('676.7.6.7', 676767)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
