import logging
import sys
import unittest
import zmq

from test import support

from mdbase.broker import Service, Worker, MajorDomoBroker

log = logging.getLogger()
log.addHandler(logging.StreamHandler(sys.stdout))

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
    def test_process_client(self):
        """Test process client method"""
        pass

    def test_require_worker(self):
        """Test require worker method"""
        address = b"tcp://localhost:6666"
        self.assertEqual(len(self.broker.workers), 0)
        worker = self.broker.require_worker(address)
        self.assertEqual(len(self.broker.workers), 1)
        self.assertEqual(worker.address, address)

    @unittest.skip("building up to it")
    def test_process_worker(self):
        """Test process worker method"""
        pass

    @unittest.skip("building up to it")
    def test_delete_worker(self):
        """Test delete worker method"""
        pass

    def test_require_service(self):
        """Test require service method"""
        service = b"W_ECHO"
        address = b"tcp://localhost:6666"
        self.assertEqual(len(self.broker.services), 0)
        worker = self.broker.require_worker(address)
        worker.service = self.broker.require_service(service)
        self.assertEqual(len(self.broker.services), 1)
        self.assertIn(service, self.broker.services.keys())
        self.assertIn(worker.service, self.broker.services.values())
        self.assertIsInstance(self.broker.services[service], Service)

    @unittest.skip("building up to it")
    def test_service_internal(self):
        """Test service internal method"""
        pass

    @unittest.skip("building up to it")
    def test_send_heartbeats(self):
        """Test send heartbeats method"""
        pass

    @unittest.skip("building up to it")
    def test_purge_workers(self):
        """Test purge workers method"""
        pass

    @unittest.skip("building up to it")
    def test_worker_waiting(self):
        """Test worker waiting method"""
        pass

    @unittest.skip("building up to it")
    def test_dispatch(self):
        """Test dispatch method"""
        pass

    @unittest.skip("building up to it")
    def test_send_to_worker(self):
        """Test send to worker method"""
        pass


if __name__ == '__main__':
    unittest.main()