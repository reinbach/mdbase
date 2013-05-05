import unittest
import zmq

from mdbase import constants
from mdbase.broker import MajorDomoBroker
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

    @unittest.skip("determine how to mock the necessary parts")
    def test_send_to_broker_model(self):
        """Test send message to broker"""
        b = MajorDomoBroker(False)
        w = MajorDomoWorker(self.broker_url, b"echo", False)
        w.send_to_broker(constants.W_REQUEST, b.service, [b"test"])

    @unittest.skip("need to test send to broker method first")
    def test_reconnect_to_broker_model(self):
        """Test reconnecting to broker"""
        b = MajorDomoBroker(False)
        w = MajorDomoWorker(self.broker_url, b"echo", False)
        