import unittest
import zmq

from mdbase.client import MajorDomoClient

class TestClient(unittest.TestCase):

    def setUp(self):
        self.broker_url = "tcp://localhost:6666"

    def test_instantiate(self):
        """Test instantiating client"""
        c = MajorDomoClient(self.broker_url)
        self.assertEqual(c.broker, self.broker_url)
        self.assertFalse(c.verbose)
        self.assertIsInstance(c.ctx, zmq.Context)
        self.assertIsInstance(c.poller, zmq.Poller)

    def test_verbose(self):
        """Test setting of verbose on client"""
        c = MajorDomoClient(self.broker_url, True)
        self.assertEqual(c.broker, self.broker_url)
        self.assertTrue(c.verbose)
        self.assertIsInstance(c.ctx, zmq.Context)
        self.assertIsInstance(c.poller, zmq.Poller)

if __name__ == "__main__":
    unittest.main()