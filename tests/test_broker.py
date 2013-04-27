import unittest

from mdbase.broker import Service, Worker

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

if __name__ == '__main__':
    unittest.main()