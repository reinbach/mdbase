import logging
import sys
import time
import unittest
import zmq

from test import support

from mdbase.broker import Service, Worker, MajorDomoBroker, W_READY

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
        self.broker = MajorDomoBroker()
        self.broker_verbose = MajorDomoBroker(True)
        self.address = b"tcp://localhost:6666"
        self.service = b"S_ECHO"

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
        b = MajorDomoBroker(False)
        b.destroy()
        #TODO ensure workers list is cleared

    @unittest.skip("building up to it")
    def test_process_client(self):
        """Test process client method"""
        pass

    def test_require_worker(self):
        """Test require worker method"""
        self.assertEqual(len(self.broker.workers), 0)
        worker = self.broker.require_worker(self.address)
        self.assertEqual(len(self.broker.workers), 1)
        self.assertEqual(worker.address, self.address)

        # verbose
        worker = self.broker_verbose.require_worker(self.address)
        self.assertEqual(len(self.broker_verbose.workers), 1)

    @unittest.skip("building up to it")
    def test_process_worker(self):
        """Test process worker method"""
        pass

    def test_delete_worker(self):
        """Test delete worker method"""
        self.assertEqual(len(self.broker.workers), 0)
        worker = self.broker.require_worker(self.address)
        self.assertEqual(len(self.broker.workers), 1)

        # delete but no disconnect
        self.broker.delete_worker(worker, False)
        self.assertEqual(len(self.broker.workers), 0)

        # test when worker service is set
        worker = self.broker.require_worker(self.address)
        worker.service = self.broker.require_service(self.service)
        self.broker.worker_waiting(worker)
        self.assertEqual(len(self.broker.workers), 1)
        self.broker.delete_worker(worker, False)
        self.assertEqual(len(self.broker.workers), 0)

    def test_delete_worker_disconnect(self):
        """Test delete worker method with disconnect call to worker"""
        self.assertEqual(len(self.broker.workers), 0)
        worker = self.broker.require_worker(self.address)
        self.assertEqual(len(self.broker.workers), 1)

        # delete and disconnect
        self.broker.delete_worker(worker, True)
        self.assertEqual(len(self.broker.workers), 0)

    @unittest.skip("need work service to not be none")
    def test_delete_worker_service(self):
        """Test delete worker method with service not none"""
        pass

    def test_require_service(self):
        """Test require service method"""
        self.assertEqual(len(self.broker.services), 0)
        worker = self.broker.require_worker(self.address)
        worker.service = self.broker.require_service(self.service)
        self.assertEqual(len(self.broker.services), 1)
        self.assertIn(self.service, self.broker.services.keys())
        self.assertIn(worker.service, self.broker.services.values())
        self.assertIsInstance(self.broker.services[self.service], Service)

    def test_service_internal(self):
        """Test service internal method"""
        self.broker.service_internal(b"mmi.service", [b"", b"Hello"])

    def test_send_heartbeats(self):
        """Test send heartbeats method"""
        worker = self.broker.require_worker(self.address)
        worker.service = self.broker.require_service(self.service)
        self.broker.worker_waiting(worker)

        cur_heatbeat_at = self.broker.heartbeat_at
        self.broker.heartbeat_at = time.time() - 10
        self.broker.send_heartbeats()
        self.assertTrue(self.broker.heartbeat_at > cur_heatbeat_at)

    def test_purge_workers(self):
        """Test purge workers method"""
        worker1 = self.broker.require_worker(self.address)
        worker1.service = self.broker.require_service(self.service)

        worker2 = self.broker.require_worker(b"tcp://localhost:6667")
        worker2.service = self.broker.require_service(b"S_LOG")

        self.broker.worker_waiting(worker1)
        self.broker.worker_waiting(worker2)

        self.assertEqual(len(self.broker.waiting), 2)

        # modify expiry to be in past for worker1
        worker1.expiry = time.time() - 1

        self.broker.purge_workers()
        self.assertEqual(len(self.broker.waiting), 1)

    def test_worker_waiting(self):
        """Test worker waiting method"""
        worker = self.broker.require_worker(self.address)
        worker.service = self.broker.require_service(self.service)
        self.assertEqual(len(self.broker.waiting), 0)
        self.assertEqual(len(worker.service.waiting), 0)
        self.broker.worker_waiting(worker)
        self.assertEqual(len(self.broker.waiting), 1)
        self.assertEqual(len(worker.service.waiting), 1)

    @unittest.skip("building up to it")
    def test_dispatch(self):
        """Test dispatch method"""
        pass

    def test_send_to_worker(self):
        """Test send to worker method"""
        worker = self.broker.require_worker(self.address)
        self.assertIsNone(self.broker.send_to_worker(worker, W_READY, None))
        self.assertIsNone(self.broker.send_to_worker(worker, W_READY, None, b'Hello'))
        self.assertIsNone(self.broker.send_to_worker(worker, W_READY, b'Hello'))

        worker = self.broker_verbose.require_worker(self.address)

        with support.captured_stdout() as s:
            self.assertIsNone(self.broker_verbose.send_to_worker(worker, W_READY, None))
            self.assertIn("{addr}".format(addr=self.address), s.getvalue())


if __name__ == '__main__':
    unittest.main()