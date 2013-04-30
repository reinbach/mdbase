import unittest
import zmq

from mdbase.worker import MajorDomoWorker


class TestMajorDomoWorker(unittest.TestCase):

    def setUp(self):
        self.broker_url = "tcp://localhost:6666"

    def test_instantiate(self):
        """Test instantiating worker model"""
        service_name = b"echo"
        verbose = False
        w = MajorDomoWorker(self.broker_url, service_name, verbose)
        self.assertEqual(w.broker, self.broker_url)
        self.assertEqual(w.service, service_name)
        self.assertEqual(w.verbose, verbose)
        self.assertIsInstance(w.ctx, zmq.Context)
        self.assertIsInstance(w.poller, zmq.Poller)
