import importlib.util
import pathlib
import threading
import unittest
import urllib.request

HERE=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("openvisio_server",HERE/"openvisio_server.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class WindowsLauncherTests(unittest.TestCase):
    def test_serves_app_on_loopback(self):
        server=module.make_server(0)
        self.assertEqual(server.server_address[0],"127.0.0.1")
        worker=threading.Thread(target=server.serve_forever,daemon=True)
        worker.start()
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}/",timeout=4) as resp:
                body=resp.read().decode("utf-8")
                self.assertEqual(resp.status,200)
                self.assertIn("OpenVisio",body)
                self.assertEqual(resp.headers["X-Content-Type-Options"],"nosniff")
            with urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}/src/main.js",timeout=4) as resp:
                self.assertEqual(resp.status,200)
                self.assertIn(b"import",resp.read())
        finally:
            server.shutdown();server.server_close();worker.join(timeout=3)
    def test_missing_path_returns_404(self):
        server=module.make_server(0)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            with self.assertRaises(urllib.error.HTTPError) as cm:
                urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}/missing-107.txt",timeout=4)
            self.assertEqual(cm.exception.code,404)
        finally:
            server.shutdown();server.server_close();worker.join(timeout=3)
if __name__=="__main__":unittest.main()
