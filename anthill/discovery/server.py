
from anthill.common import handler, server, access, sign, discover

from . model.discovery import DiscoveryModel, ServiceNotFound
from . import handler as h
from . import admin
from . import options as _opts


class DiscoveryServer(server.Server):
    def __init__(self):
        super(DiscoveryServer, self).__init__()

        self.services = DiscoveryModel(self)

    def get_admin(self):
        return {
            "index": admin.RootAdminController,
            "service": admin.ServiceController,
            "new_service": admin.NewServiceController,
            "clone_service": admin.CloneServiceController,
            "services": admin.ServicesController
        }

    def get_models(self):
        return [self.services]

    def get_metadata(self):
        return {
            "title": "Discovery",
            "description": "Map each service location dynamically",
            "icon": "map-signs"
        }

    def get_handlers(self):
        return [
            (r"/@service/(.*?)/(.*)", h.ServiceInternalHandler),
            (r"/@services/(.*)", h.ServiceListInternalHandler),

            (r"/service/(.*?)/(.*)", h.DiscoverNetworkHandler),
            (r"/services/(.*?)/(.*)", h.MultiDiscoverNetworkHandler),
            (r"/service/(.*)", h.DiscoverHandler),
            (r"/services/(.*)", h.MultiDiscoverHandler),
        ]

    def get_internal_handler(self):
        return h.InternalHandler(self)

    async def get_auth_location(self, network):
        try:
            location = await self.services.get_service("login", network)
        except ServiceNotFound:
            location = None

        return location

    def init_discovery(self):
        discover.cache = self.services


if __name__ == "__main__":

    stt = server.init()
    access.AccessToken.init([access.public()])
    server.start(DiscoveryServer)
