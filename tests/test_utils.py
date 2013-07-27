import pytest
import zmq

from test import support

from mdbase.utils import dump, zpipe

BUFFER = "-" * 40


@pytest.fixture
def ctx():
    return zmq.Context()

class TestUtils():
    def test_dump(self):
        """Test dump function"""
        msg = ['hello']
        with support.captured_stdout() as s:
            dump(msg)
        assert "%s\n%s\n" % (BUFFER, "[005]\nhello") == s.getvalue()

    def test_dump_multipart(self):
        """Test dump function"""
        msg = ['hello', 'world']
        with support.captured_stdout() as s:
            dump(msg)
        assert "%s\n%s\n" % (BUFFER, "[005]\nhello\n[005]\nworld") == s.getvalue()

    def test_dump_non_ascii(self):
        """Test dump of non ascii chars"""
        msg = ['ã']
        with support.captured_stdout() as s:
            dump(msg)
        assert "%s\n%s\n%s\n" % (BUFFER, "[001]", msg[0]) == s.getvalue()

    def test_zpipe(self, ctx):
        """Test zpipe method

        Setting up two inproc PAIRs for threading
        """
        s1, s2 = zpipe(ctx)

        # check high water mark setting
        assert s1.get_hwm() == 1
        assert s2.get_hwm() == 1

        # check linger setting
        assert s1.get(zmq.LINGER) == 0
        assert s2.get(zmq.LINGER) == 0

        # check sending message between pair
        msg = [b'', b'hello']
        s1.send_multipart(msg)
        resp = s2.recv_multipart()
        assert msg == resp
