import unittest
import zmq

from test import support

from mdbase.utils import dump, zpipe

BUFFER = "-" * 40

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.ctx = zmq.Context()

    def tearDown(self):
        self.ctx.destroy()

    def test_dump(self):
        """Test dump function"""
        msg = ['hello']
        with support.captured_stdout() as s:
            dump(msg)
        self.assertEqual("%s\n%s\n" % (BUFFER, "[005]\nhello"), s.getvalue())

    def test_dump_multipart(self):
        """Test dump function"""
        msg = ['hello', 'world']
        with support.captured_stdout() as s:
            dump(msg)
        self.assertEqual(
            "%s\n%s\n" % (BUFFER, "[005]\nhello\n[005]\nworld"),
            s.getvalue()
        )

    def test_dump_non_ascii(self):
        """Test dump of non ascii chars"""
        msg = ['ã']
        with support.captured_stdout() as s:
            dump(msg)
        self.assertEqual(
            "%s\n%s\n%s\n" % (BUFFER, "[001]", msg[0]),
            s.getvalue()
        )

    def test_zpipe(self):
        """Test zpipe method

        Setting up two inproc PAIRs for threading
        """
        s1, s2 = zpipe(self.ctx)

        # check high water mark setting
        self.assertEqual(s1.get_hwm(), 1)
        self.assertEqual(s2.get_hwm(), 1)

        # check linger setting
        self.assertEqual(s1.get(zmq.LINGER), 0)
        self.assertEqual(s2.get(zmq.LINGER), 0)

        # check sending message between pair
        msg = [b'', b'hello']
        s1.send_multipart(msg)
        resp = s2.recv_multipart()
        self.assertEqual(msg, resp)

if __name__ == "__main__":
    unittest.main()