import http.server
import socketserver
import re

serverPort = int(os.environ.get("SERVER_PORT", 8765))
token = os.environ.get("TOKEN", "your_token")
hostsFile = os.environ.get("HOSTS_FILE", "hosts.txt")
webPath = os.environ.get("WEBPATH", "/update")


# Define the handler to use (SimpleHTTPRequestHandler is provided by http.server)
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Check if the request is for the /update endpoint
        if self.path.startswith(webPath):
            self.recordUpdate()
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid request(0)")
    
    def recordUpdate(self):
        # chk token
        if not self.check_token():
            return
        # chk domain
        domain = self.get_query_param("zone")
        if not domain:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid request(3)")
            return
        # chk ip
        # get ip from "ipv4" or "ipv6" param
        if "ipv4" in self.path:
            ip = self.get_query_param("ipv4")
        elif "ipv6" in self.path:
            ip = self.get_query_param("ipv6")
        elif "ip" in self.path:
            ip = self.get_query_param("ip")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid request(4)")
            return
        # update record
        with open(hostsFile, "r") as f:
            content = f.read()
        pattern = rf'({re.escape(domain)}\s+)(\d+\.\d+\.\d+\.\d+)'
        match = re.search(pattern, content)
        if match:
            # replace the ip of existing domain
            content = content[:match.start(2)] + ip + content[match.end(2):]
        else:
            # add a new record
            #content += f"\n{ip} {domain}"
            content += f"\n{domain} {ip}"

        try:
            with open(hostsFile, "w") as f:
                f.write(content)
            self.send_response(200, "OK")
            self.end_headers()
            self.wfile.write(b"OK")
        except:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"host file not writable")

    def get_query_param(self, param_name):
        # Helper function to extract a parameter value from the query string
        param_value = ""
        if param_name in self.path:
            param_value = self.path.split(f"{param_name}=")[1].split("&")[0]
        return param_value
    
    def check_token(self):
        # chk if the token exists in the query string
        if "token" not in self.path:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid request(2)")
            return False
        else:
            provided_token = self.get_query_param("token")
            if provided_token == token:
                #super().do_GET()
                return True
            else:
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Invalid request(1)")
                return False
            
# Set up the server
with socketserver.TCPServer(("", serverPort), MyHandler) as httpd:
    try:
        print(f"Server started on port {serverPort}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped")
        httpd.server_close()