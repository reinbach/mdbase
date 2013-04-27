import unittest

from test import support

from mdbase.utils import dump

BUFFER = "-" * 40

class TestUtils(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()