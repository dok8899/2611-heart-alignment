import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock


ROOT = Path(__file__).resolve().parent
MEMBERS = [
    {"id": 1, "name": "林晨曦", "age": 32, "membership": "年度會員"},
    {"id": 2, "name": "陳以安", "age": 35, "membership": "城市體驗"},
    {"id": 3, "name": "周予晴", "age": 29, "membership": "年度會員"},
    {"id": 4, "name": "王知遠", "age": 38, "membership": "體驗會員"},
    {"id": 5, "name": "許書妍", "age": 31, "membership": "城市體驗"},
]
MEMBERS_LOCK = Lock()


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, data: object) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            body = (ROOT / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/members":
            with MEMBERS_LOCK:
                members = list(MEMBERS)
            self.send_json(200, members)
        else:
            self.send_json(404, {"error": "Not Found"})

    def do_POST(self) -> None:
        if self.path != "/api/members":
            self.send_json(404, {"error": "Not Found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 16_384:
                raise ValueError("Request body must be between 1 and 16384 bytes.")
            payload = json.loads(self.rfile.read(content_length))
            name = payload.get("name")
            age = payload.get("age")
            membership = payload.get("membership")
            if not isinstance(name, str) or not name.strip() or len(name.strip()) > 80:
                raise ValueError("name 為必填，且最多 80 個字元。")
            if isinstance(age, bool) or not isinstance(age, int) or not 18 <= age <= 100:
                raise ValueError("age 必須是 18 至 100 的整數。")
            allowed_memberships = {"體驗會員", "城市體驗", "年度會員"}
            if not isinstance(membership, str) or membership not in allowed_memberships:
                raise ValueError("membership 必須是體驗會員、城市體驗或年度會員。")
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError, AttributeError) as error:
            self.send_json(400, {"error": str(error) or "Invalid JSON body."})
            return

        with MEMBERS_LOCK:
            member = {
                "id": max((item["id"] for item in MEMBERS), default=0) + 1,
                "name": name.strip(),
                "age": age,
                "membership": membership,
            }
            MEMBERS.append(member)
        self.send_json(201, member)


if __name__ == "__main__":
    host, port = "127.0.0.1", 8000
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Serving page at http://localhost:{port}/", flush=True)
    print(f"Members API: http://localhost:{port}/api/members", flush=True)
    server.serve_forever()
