#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import pickle

forbidden = b"".join([pickle.REDUCE, pickle.INST, pickle.OBJ, pickle.NEWOBJ, pickle.NEWOBJ_EX])

class Handler(BaseHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)

        if any(byte in forbidden for byte in body):
            self.send_response(500)
            self.end_headers()
            return
    
        result = str(pickle.loads(body)).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", len(result))
        self.end_headers()
        self.wfile.write(result)

def main(host="0.0.0.0", port=8000):
    with HTTPServer((host, port), Handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    main()