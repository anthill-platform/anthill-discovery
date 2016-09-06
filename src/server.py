
from tornado.gen import coroutine, Return

import common.handler
import common.server
import common.access
import common.sign
import common.discover

from model.discovery import DiscoveryModel, ServiceNotFound

import handler
import admin
import options as _opts


class DiscoveryServer(common.server.Server):
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
            (r"/@service/(.*?)/(.*)", handler.ServiceInternalHandler),
            (r"/@services/(.*)", handler.ServiceListInternalHandler),

            (r"/service/(.*?)/(.*)", handler.DiscoverNetworkHandler),
            (r"/services/(.*?)/(.*)", handler.MultiDiscoverNetworkHandler),
            (r"/service/(.*)", handler.DiscoverHandler),
            (r"/services/(.*)", handler.MultiDiscoverHandler),
        ]

    def get_internal_handler(self):
        return handler.InternalHandler(self)

    @coroutine
    def get_auth_location(self, network):
        try:
            location = yield self.services.get_service("login", network)
        except ServiceNotFound:
            location = None

        raise Return(location)

    def init_discovery(self):
        common.discover.cache = self.services

if __name__ == "__main__":

    stt = common.server.init()
    common.access.AccessToken.init([common.access.public()])
    common.server.start(DiscoveryServer)
