"""OpenVisio local server. Author: Abdelhalim Talbi. Python standard library only."""
import argparse
import functools
import http.server
import pathlib
import socket
import sys
import threading
import webbrowser

ROOT = pathlib.Path(__file__).resolve().parent.parent

class OpenVisioHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

def make_server(port=0):
    return http.server.ThreadingHTTPServer(("127.0.0.1", port), OpenVisioHandler)

def main(argv=None):
    parser=argparse.ArgumentParser(description="Launch OpenVisio on Windows")
    parser.add_argument("--port", type=int, default=0, help="Local port (0: automatic)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser")
    args=parser.parse_args(argv)
    if not 0 <= args.port <= 65535: parser.error("port must be between 0 and 65535")
    try: server=make_server(args.port)
    except OSError as exc:
        print(f"Unable to start OpenVisio: {exc}",file=sys.stderr)
        return 1
    url=f"http://127.0.0.1:{server.server_port}/"
    print("OpenVisio v10.7 - Abdelhalim Talbi", flush=True)
    print(f"Open your browser at: {url}", flush=True)
    print("Press Ctrl+C to stop.",flush=True)
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try: server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt: pass
    finally: server.server_close()
    return 0

if __name__=="__main__": raise SystemExit(main())
