
import common.keyvalue

from tornado.gen import coroutine, Return, Task
from common.options import options
from common.model import Model


class DiscoveryModel(Model):

    INTERNAL = "internal"
    EXTERNAL = "external"
    BROKER = "broker"

    NETWORKS = [INTERNAL, EXTERNAL, BROKER]

    def __init__(self, application):
        self.application = application

        self.kv = common.keyvalue.KeyValueStorage(
            host=options.discover_services_host,
            port=options.discover_services_port,
            db=options.discover_services_db)

    @coroutine
    def delete_service(self, service_id):
        db = self.kv.acquire()

        try:
            yield Task(db.delete, service_id)
        finally:
            yield db.release()

    @coroutine
    def delete_service_network(self, service_id, network):
        db = self.kv.acquire()
        try:
            yield Task(
                db.hdel,
                service_id,
                network)
        finally:
            yield db.release()

    @coroutine
    def list_all_services(self, network):

        db = self.kv.acquire()
        try:
            keys = yield Task(db.keys, "*")

            services = {}
            for key in keys:
                location = yield Task(
                    db.hget,
                    key,
                    network)

                services[key] = location
        finally:
            yield db.release()

        raise Return(services)

    @coroutine
    def get_service(self, service_id, network, **ignored):

        db = self.kv.acquire()
        try:
            service = yield Task(
                db.hget,
                service_id,
                network)

            if not service:
                raise ServiceNotFound(service_id)
        finally:
            yield db.release()

        raise Return(service)

    @coroutine
    def list_service_networks(self, service_id):

        db = self.kv.acquire()
        try:
            services = yield Task(
                db.hgetall,
                service_id)

            if not services:
                raise ServiceNotFound(service_id)
        finally:
            yield db.release()

        raise Return(services or {})

    @coroutine
    def list_services(self, service_ids, network):

        db = self.kv.acquire()
        try:
            service_locations = {}

            for service_id in service_ids:
                service = yield Task(
                    db.hget,
                    service_id,
                    network)

                if service is None or len(service) == 0:
                    raise ServiceNotFound(service_id)
                else:
                    service_locations[service_id] = service
        finally:
            yield db.release()

        raise Return(service_locations)

    @coroutine
    def set_service(self, service_id, service_location, network):

        db = self.kv.acquire()
        try:
            yield Task(
                db.hset,
                service_id,
                network,
                service_location)
        finally:
            yield db.release()

    @coroutine
    def set_service_networks(self, service_id, networks):

        db = self.kv.acquire()
        try:

            yield Task(db.delete, service_id)

            for network, service_location in networks.iteritems():
                yield Task(
                    db.hset,
                    service_id,
                    network,
                    service_location)
        finally:
            yield db.release()


class ServiceNotFound(Exception):
    def __init__(self, service_id):
        self.service_id = service_id
