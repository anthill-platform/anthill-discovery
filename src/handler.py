
import ujson

from common.access import internal, InternalError
from common.handler import JsonHandler, CORSHandlerMixin
from model.discovery import ServiceNotFound, DiscoveryModel

from tornado.web import HTTPError
from tornado.gen import coroutine, Return


class DiscoverServiceHandler(CORSHandlerMixin, JsonHandler):
    def wrap(self, service):
        if self.application.api_version:
            return service + "/v" + self.application.api_version
        return service


class DiscoverHandler(DiscoverServiceHandler):
    @coroutine
    def get(self, service_name):

        try:
            service = yield self.application.services.get_service(
                service_name,
                DiscoveryModel.EXTERNAL)

        except ServiceNotFound:
            raise HTTPError(
                404,
                "Service '{0}' was not found".format(service_name))

        if self.get_argument("version", "true") == "true":
            self.write(self.wrap(service))
        else:
            self.write(service)


class DiscoverNetworkHandler(DiscoverServiceHandler):
    @coroutine
    @internal
    def get(self, service_name, network):

        try:
            service = yield self.application.services.get_service(
                service_name,
                network)

        except ServiceNotFound:
            raise HTTPError(
                404,
                "Service '{0}' was not found".format(service_name))

        if self.get_argument("version", "true") == "true":
            self.write(self.wrap(service))
        else:
            self.write(service)


class MultiDiscoverHandler(DiscoverServiceHandler):
    @coroutine
    def get(self, service_names):

        try:
            service_ids = yield self.application.services.list_services(
                service_names.split(","),
                DiscoveryModel.EXTERNAL)

        except ServiceNotFound as e:
            raise HTTPError(404, "Service '{0}' was not found".format(e.service_id))

        if self.get_argument("version", "true") == "true":
            self.dumps({
                service: self.wrap(location)
                for service, location in service_ids.iteritems()
            })
        else:
            self.dumps(service_ids)


class MultiDiscoverNetworkHandler(DiscoverServiceHandler):
    @coroutine
    @internal
    def get(self, service_names, network):

        services_ids = filter(
            bool,
            service_names.split(","))

        try:
            service_ids = yield self.application.services.list_services(
                services_ids,
                network)

        except ServiceNotFound as e:
            raise HTTPError(
                404,
                "Service '{0}' was not found".format(e.service_id))

        if self.get_argument("version", "true") == "true":
            self.dumps({
                service: self.wrap(location)
                for service, location in service_ids.iteritems()
            })
        else:
            self.write(service_ids)


class ServiceInternalHandler(JsonHandler):
    @coroutine
    @internal
    def get(self, service_id, network):
        try:
            service = yield self.application.services.get_service(
                service_id,
                network)

        except ServiceNotFound:
            raise HTTPError(
                400, "No such service")

        self.dumps({
            "id": service_id,
            "location": service
        })

    @coroutine
    @internal
    def post(self, service_id, network):
        service_location = self.get_argument("location")

        yield self.application.services.set_service(
            service_id,
            service_location,
            network)

        self.dumps({"result": "OK"})


class ServiceListInternalHandler(JsonHandler):
    @coroutine
    @internal
    def get(self, network):

        services_list = yield self.application.services.list_all_services(network)

        self.dumps(services_list)


class InternalHandler(object):
    def __init__(self, application):
        self.application = application

    @coroutine
    def get_service(self, service_id, network=None, version=True):

        services = self.application.services

        try:
            if network:
                data = yield services.get_service(services, network=network)
            else:
                data = yield services.list_service_networks(service_id)
        except ServiceNotFound:
            raise InternalError(404, "Service not found!")

        raise Return(data)

    @coroutine
    def set_service(self, service_id, network, location):
        services = self.application.services

        yield services.set_service(service_id, location, network=network)

        raise Return("OK")
