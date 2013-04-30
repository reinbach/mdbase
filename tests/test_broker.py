import unittest
import zmq

from mdbase.broker import Service, Worker, MajorDomoBroker

class TestBrokerService(unittest.TestCase):
    def test_service_instantiate(self):
        """Test instantiating service model"""
        name = "Service1"
        s = Service(name)
        self.assertFalse(s.requests)
        self.assertFalse(s.waiting)
        self.assertEqual(s.name, name)

class TestBrokerWorker(unittest.TestCase):
    def test_worker_instantiate(self):
        """Test instantiating worker model"""
        identity = hex(1)
        address = "worker1"
        expiry = 3
        w = Worker(identity, address, expiry)
        self.assertIsNone(w.service)
        self.assertEqual(w.identity, identity)
        self.assertEqual(w.address, address)
        self.assertIsNotNone(w.expiry)

class TestBrokerModel(unittest.TestCase):
    def setUp(self):
        self.broker = MajorDomoBroker(False)

    def test_broker_instantiate(self):
        """Test instantiating majordomo worker model"""
        verbose = True

        b = MajorDomoBroker(verbose)
        self.assertEqual(b.verbose, verbose)
        self.assertEqual(b.services, {})
        self.assertEqual(b.workers, {})
        self.assertEqual(b.waiting, [])
        self.assertTrue(b.heartbeat_at)
        self.assertIsInstance(b.ctx, zmq.Context)
        self.assertTrue(b.socket)
        self.assertEqual(b.socket.linger, 0)
        self.assertIsInstance(b.poller, zmq.Poller)

    @unittest.skip("builing up to it")
    def test_broker_destroy(self):
        """Test destroy broker method"""
        verbose = True
        b = MajorDomoBroker(verbose)
        b.destroy()
        #TODO ensure workers list is cleared

    @unittest.skip("building up to it")
    def test_require_worker(self):
        """Test require worker method"""
        pass

if __name__ == '__main__':
    unittest.main()