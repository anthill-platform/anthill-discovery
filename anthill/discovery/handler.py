
from anthill.common.access import internal, InternalError
from anthill.common.handler import JsonHandler
from . model.discovery import ServiceNotFound, DiscoveryModel

from tornado.web import HTTPError


class DiscoverServiceHandler(JsonHandler):
    # noinspection PyMethodMayBeStatic
    def wrap(self, service):
        return service


class DiscoverHandler(DiscoverServiceHandler):
    async def get(self, service_name):
        try:
            service = await self.application.services.get_service(service_name, DiscoveryModel.EXTERNAL)
        except ServiceNotFound:
            raise HTTPError(404, "Service '{0}' was not found".format(service_name))
        self.write(service)


class DiscoverNetworkHandler(DiscoverServiceHandler):
    @internal
    async def get(self, service_name, network):
        try:
            service = await self.application.services.get_service(service_name, network)
        except ServiceNotFound:
            raise HTTPError(404, "Service '{0}' was not found".format(service_name))
        self.write(service)


class MultiDiscoverHandler(DiscoverServiceHandler):
    async def get(self, service_names):
        try:
            service_ids = await self.application.services.list_services(
                service_names.split(","), DiscoveryModel.EXTERNAL)
        except ServiceNotFound as e:
            raise HTTPError(404, "Service '{0}' was not found".format(e.service_id))
        self.dumps(service_ids)


class MultiDiscoverNetworkHandler(DiscoverServiceHandler):
    @internal
    async def get(self, service_names, network):

        services_ids = filter(
            bool,
            service_names.split(","))

        try:
            service_ids = await self.application.services.list_services(
                services_ids,
                network)

        except ServiceNotFound as e:
            raise HTTPError(
                404,
                "Service '{0}' was not found".format(e.service_id))

        self.dumps(service_ids)


class ServiceInternalHandler(JsonHandler):
    @internal
    async def get(self, service_id, network):
        try:
            service = await self.application.services.get_service(
                service_id,
                network)

        except ServiceNotFound:
            raise HTTPError(
                400, "No such service")

        self.dumps({
            "id": service_id,
            "location": service
        })

    @internal
    async def post(self, service_id, network):
        service_location = self.get_argument("location")

        await self.application.services.set_service(
            service_id,
            service_location,
            network)

        self.dumps({"result": "OK"})


class ServiceListInternalHandler(JsonHandler):
    @internal
    async def get(self, network):

        services_list = await self.application.services.list_all_services(network)

        self.dumps(services_list)


class InternalHandler(object):
    def __init__(self, application):
        self.application = application

    async def get_service(self, service_id, network=None):

        services = self.application.services

        try:
            if network:
                data = await services.get_service(services, network=network)
            else:
                data = await services.list_service_networks(service_id)
        except ServiceNotFound:
            raise InternalError(404, "Service not found!")

        return data

    async def set_service(self, service_id, network, location):
        services = self.application.services

        await services.set_service(service_id, location, network=network)

        return "OK"
