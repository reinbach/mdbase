import logging
import pytest
import sys
import time
import zmq

from mock import Mock, patch
from test import support

from mdbase.broker import (Service, Worker, MajorDomoBroker, W_READY, W_REQUEST, W_DISCONNECT,
                           W_HEARTBEAT, W_REPLY, C_CLIENT)

log = logging.getLogger()
log.addHandler(logging.StreamHandler(sys.stdout))


@pytest.fixture
def broker():
    return MajorDomoBroker()


@pytest.fixture
def broker_verbose():
    return MajorDomoBroker(True)


@pytest.fixture
def address():
    return b"tcp://localhost:6666"


@pytest.fixture
def service():
    return Service(b"S_ECHO")


class TestBrokerService():
    def test_service_instantiate(self):
        """Test instantiating service model"""
        name = "Service1"
        s = Service(name)
        assert s.requests == []
        assert s.waiting == []
        assert s.name == name


class TestBrokerWorker():
    def test_worker_instantiate(self):
        """Test instantiating worker model"""
        identity = hex(1)
        address = "worker1"
        expiry = 3
        w = Worker(identity, address, expiry)
        assert w.service is None
        assert w.identity == identity
        assert w.address == address
        assert w.expiry is not None


class TestBrokerModel():
    def test_broker_instantiate(self):
        """Test instantiating majordomo worker model"""
        verbose = True

        b = MajorDomoBroker(verbose)
        assert b.verbose == verbose
        assert b.services == {}
        assert b.workers == {}
        assert b.waiting == []
        assert b.heartbeat_at
        assert isinstance(b.ctx, zmq.Context)
        assert b.socket
        assert b.socket.linger == 0
        assert isinstance(b.poller, zmq.Poller)

    def test_broker_destroy(self, address):
        """Test destroy broker method"""
        b = MajorDomoBroker(False)
        b.require_worker(address)
        assert len(b.workers) == 1
        b.destroy()
        assert len(b.workers) == 0

    def test_process_client(self, broker):
        """Test process client method with service internal"""
        service_internal_mock = Mock()
        broker.service_internal = service_internal_mock
        broker.process_client("TEST", [broker.INTERNAL_SERVICE_PREFIX, "hello"])
        service_internal_mock.assert_called_with(broker.INTERNAL_SERVICE_PREFIX, ["TEST", "", "hello"])

    def test_process_client_dispatch(self, broker):
        """Test process client method with service internal"""
        dispatch_mock = Mock()
        broker.dispatch = dispatch_mock
        broker.process_client("TEST", ["srv1", "hello"])
        dispatch_mock.assert_called_with(broker.require_service("srv1"), ["TEST", "", "hello"])

    def test_require_worker(self, broker, broker_verbose, address):
        """Test require worker method"""
        assert len(broker.workers) == 0
        worker = broker.require_worker(address)
        assert len(broker.workers) == 1
        assert worker.address == address

        # verbose
        worker = broker_verbose.require_worker(address)
        assert len(broker_verbose.workers) == 1

    def test_process_worker(self, broker, address):
        """Test process worker method without recognized command"""
        with support.captured_stdout() as s:
            broker.process_worker(address, [W_REQUEST, b"hello"])
            assert "hello" in s.getvalue()

        mock_dump = Mock()
        with patch('mdbase.broker.dump', mock_dump):
            broker.process_worker(address, [W_REQUEST, b"hello"])
            mock_dump.assert_called_with([b"hello"])

    def test_process_worker_disconnect(self, broker, address):
        """Test process worker method with disconnect command"""
        mock_delete = Mock()
        broker.delete_worker = mock_delete
        broker.process_worker(address, [W_DISCONNECT, b"hello"])
        mock_delete.assert_called_with(broker.require_worker(address), False)

    def test_process_worker_heartbeat(self, broker, address):
        """Test process worker method with heartbeat command"""
        mock_delete = Mock()
        broker.delete_worker = mock_delete
        broker.process_worker(address, [W_HEARTBEAT, b"hello"])
        mock_delete.assert_called_with(broker.require_worker(address), True)

    def test_process_worker_heartbeat_worker_ready(self, broker, address):
        """Test process worker method with heartbeat command and worker is ready"""
        worker = broker.require_worker(address)
        expiry = worker.expiry
        mock_delete = Mock()
        broker.delete_worker = mock_delete
        broker.process_worker(address, [W_HEARTBEAT, b"hello"])
        assert mock_delete.call_count == 0
        assert worker.expiry > expiry

    def test_process_worker_reply(self, broker, address):
        """Test process worker method with reply command"""
        mock_delete = Mock()
        broker.delete_worker = mock_delete
        broker.process_worker(address, [W_REPLY, b"CLIENT", b"", b"hello"])
        mock_delete.assert_called_with(broker.require_worker(address), True)

    def test_process_worker_reply_worker_ready(self, broker, address):
        """Test process worker method with reply command and worker is ready"""
        worker = broker.require_worker(address)
        worker.service = broker.require_service(service)
        mock_waiting = Mock()
        mock_sendmultipart = Mock()
        broker.worker_waiting = mock_waiting
        broker.socket.send_multipart = mock_sendmultipart
        broker.process_worker(address, [W_REPLY, b"CLIENT", b"", b"hello"])
        mock_waiting.assert_called_with(worker)
        mock_sendmultipart.assert_called_with([b"CLIENT", b"", C_CLIENT, worker.service.name, b"hello"])

    def test_process_worker_ready(self, broker, address):
        """Test process worker method with ready command"""
        mock_waiting = Mock()
        broker.worker_waiting = mock_waiting
        broker.process_worker(address, [W_READY, "TEST", b"hello"])
        mock_waiting.assert_called_with(broker.require_worker(address))

    def test_process_worker_ready_internal_service_prefix(self, broker, address):
        """Test process worker method with ready command and service equal to internal service prefix"""
        mock_delete = Mock()
        broker.delete_worker = mock_delete
        broker.process_worker(address, [W_READY, "mmi.test", b"hello"])
        mock_delete.assert_called_with(broker.require_worker(address), True)

    def test_process_worker_ready_worker_ready(self, broker, address):
        """Test process worker method with ready command and worker ready"""
        mock_delete = Mock()
        broker.delete_worker = mock_delete
        worker = broker.require_worker(address)
        broker.process_worker(address, [W_READY, "TEST", b"hello"])
        mock_delete.assert_called_with(worker, True)

    def test_delete_worker(self, broker, address, service):
        """Test delete worker method"""
        assert len(broker.workers) == 0
        worker = broker.require_worker(address)
        assert len(broker.workers) == 1

        # delete but no disconnect
        broker.delete_worker(worker, False)
        assert len(broker.workers) == 0

        # test when worker service is set
        worker = broker.require_worker(address)
        worker.service = broker.require_service(service)
        broker.worker_waiting(worker)
        assert len(broker.workers) == 1
        broker.delete_worker(worker, False)
        assert len(broker.workers) == 0

    def test_delete_worker_disconnect(self, broker, address):
        """Test delete worker method with disconnect call to worker"""
        assert len(broker.workers) == 0
        worker = broker.require_worker(address)
        assert len(broker.workers) == 1

        # delete and disconnect
        broker.delete_worker(worker, True)
        assert len(broker.workers) == 0

    def test_require_service(self, broker, address, service):
        """Test require service method"""
        assert len(broker.services) == 0
        worker = broker.require_worker(address)
        worker.service = broker.require_service(service)
        assert len(broker.services) == 1
        assert service in broker.services.keys()
        assert worker.service in broker.services.values()
        assert isinstance(broker.services[service], Service)

    #TODO need more testing
    def test_service_internal(self, broker):
        """Test service internal method"""
        broker.service_internal(b"mmi.service", [b"", b"Hello"])

    def test_send_heartbeats(self, broker, address, service):
        """Test send heartbeats method"""
        worker = broker.require_worker(address)
        worker.service = broker.require_service(service)
        broker.worker_waiting(worker)

        cur_heatbeat_at = broker.heartbeat_at
        broker.heartbeat_at = time.time() - 10
        broker.send_heartbeats()
        assert broker.heartbeat_at > cur_heatbeat_at

    def test_purge_workers(self, broker, address, service):
        """Test purge workers method"""
        worker1 = broker.require_worker(address)
        worker1.service = broker.require_service(service)

        worker2 = broker.require_worker(b"tcp://localhost:6667")
        worker2.service = broker.require_service(b"S_LOG")

        broker.worker_waiting(worker1)
        broker.worker_waiting(worker2)

        assert len(broker.waiting) == 2

        # modify expiry to be in past for worker1
        worker1.expiry = time.time() - 1

        broker.purge_workers()
        assert len(broker.waiting) == 1

    def test_worker_waiting(self, broker, address, service):
        """Test worker waiting method"""
        worker = broker.require_worker(address)
        worker.service = broker.require_service(service)
        assert len(broker.waiting) == 0
        assert len(worker.service.waiting) == 0
        broker.worker_waiting(worker)
        assert len(broker.waiting) == 1
        assert len(worker.service.waiting) == 1

    def test_dispatch(self, broker, address, service):
        """Test dispatch method"""
        worker = broker.require_worker(address)
        worker.service = broker.require_service(service)
        broker.worker_waiting(worker)
        assert len(worker.service.waiting) == 1
        broker.dispatch(worker.service, [b'hello'])
        assert len(worker.service.requests) == 0
        assert len(worker.service.waiting) == 0

    def test_send_to_worker(self, broker, broker_verbose, address):
        """Test send to worker method"""
        worker = broker.require_worker(address)
        assert broker.send_to_worker(worker, W_READY, None) is None
        assert broker.send_to_worker(worker, W_READY, None, b'Hello') is None
        assert broker.send_to_worker(worker, W_READY, b'Hello') is None

        worker = broker_verbose.require_worker(address)

        with support.captured_stdout() as s:
            assert broker_verbose.send_to_worker(worker, W_READY, None) is None
            assert "{addr}".format(addr=address) in s.getvalue()
