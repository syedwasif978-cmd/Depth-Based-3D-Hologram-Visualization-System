"""
Lightweight UI smoke test (Python)
- Serves the `frontend/` directory on localhost:5000 using Python's http.server
- Fetches the homepage and checks for key text matching the provided UI (no external dependencies)
"""
import http.server
import socketserver
import threading
import time
import urllib.request

PORT = 5000
ROOT = '.'

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def start_server():
    handler = SilentHandler
    httpd = socketserver.TCPServer(('127.0.0.1', PORT), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def run_check():
    url = f'http://127.0.0.1:{PORT}/'
    try:
        with urllib.request.urlopen(url, timeout=10) as res:
            html = res.read().decode('utf-8', errors='replace')
    except Exception as e:
        print('FAILED: Could not fetch page:', e)
        return 1

    checks = [
        ('logo', 'Graphite'),
        ('hero', 'The next generation'),
        ('login heading', 'Create your Graphite account'),
        ('signup', 'Sign up with GitHub')
    ]

    failed = []
    for name, text in checks:
        if text not in html:
            failed.append((name, text))

    if failed:
        print('UI smoke test FAILED. Missing items:')
        for name, text in failed:
            print(f' - {name}: expected to find "{text}"')
        return 1

    print('UI smoke test PASSED ✅')
    return 0


if __name__ == '__main__':
    print('Starting static server at http://127.0.0.1:%d' % PORT)
    httpd = start_server()
    time.sleep(0.3)
    code = run_check()
    print('Shutting down server')
    httpd.shutdown()
    httpd.server_close()
    raise SystemExit(code)
