import unittest
import socket

from  gspynext.spy_dummy_server import ServerSocketDummy

class SpwDummyServerTestCase(unittest.TestCase):
    host = '127.0.0.1'
    port = 6060

    def setUp(self):
        # TODO use different thread
        self.server: ServerSocketDummy = ServerSocketDummy.Server(host=self.host, port=self.port)

    def test_can_connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        sock.settimeout(1)
        sock.close()

    def tearDown(self):
        self.server.close()

if __name__ == '__main__':
    unittest.main()
