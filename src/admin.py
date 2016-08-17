import common.admin as a

import ujson
from tornado.gen import coroutine

from model.discovery import ServiceNotFound, DiscoveryModel


class NewServiceController(a.AdminController):
    @coroutine
    def create(self, service_id, networks):

        services = self.application.services

        try:
            networks = ujson.loads(networks)
        except (KeyError, ValueError):
            raise a.ActionError("Corrupted JSON")

        yield services.set_service_networks(service_id, networks)

        raise a.Redirect(
            "service",
            message="New service has been created",
            service_id=service_id)

    def render(self, data):
        return [
            a.breadcrumbs([
                a.link("services", "Services")
            ], "New service"),
            a.form("New service", fields={
                "service_id": a.field("Service ID", "text", "danger", "non-empty"),
                "networks": a.field(
                    "Service networks", "kv", "primary", "non-empty",
                    values={network: network for network in DiscoveryModel.NETWORKS}),
            }, methods={
                "create": a.method("Create", "primary")
            }, data=data),
            a.links("Navigate", [
                a.link("@back", "Go back")
            ])
        ]

    def scopes_read(self):
        return ["discovery_admin"]

    def scopes_write(self):
        return ["discovery_admin"]


class RootAdminController(a.AdminController):
    def render(self, data):
        return [
            a.links("Discovery service", [
                a.link("services", "Edit services", icon="wrench")
            ])
        ]

    def scopes_read(self):
        return ["discovery_admin"]

    def scopes_write(self):
        return ["discovery_admin"]


class ServiceController(a.AdminController):
    # noinspection PyUnusedLocal
    @coroutine
    def delete(self, **ignored):
        service_id = self.context.get("service_id")
        services = self.application.services

        yield services.delete_service(service_id)

        raise a.Redirect("services", message="Service has been deleted")

    @coroutine
    def get(self, service_id):

        services = self.application.services

        try:
            networks = yield services.list_service_networks(service_id)
        except ServiceNotFound:
            raise a.ActionError("No such service: " + service_id)

        result = {
            "networks": networks
        }

        raise a.Return(result)

    def render(self, data):
        return [
            a.breadcrumbs([
                a.link("services", "Services")
            ], "Service '" + self.context.get("service_id") + "'"),
            a.form("Service '{0}' information".format(self.context.get("service_id")), fields={
                "networks": a.field(
                    "Service networks", "kv", "primary", "non-empty",
                    values={network: network for network in DiscoveryModel.NETWORKS}),
            }, methods={
                "update": a.method("Update", "primary", order=1),
                "delete": a.method("Delete", "danger", order=2)
            }, data=data),
            a.links("Navigate", [
                a.link("services", "Go back"),
                a.link("new_service", "New service", "plus")
            ])
        ]

    def scopes_read(self):
        return ["discovery_admin"]

    def scopes_write(self):
        return ["discovery_admin"]

    @coroutine
    def update(self, networks):

        try:
            networks = ujson.loads(networks)
        except (KeyError, ValueError):
            raise a.ActionError("Corrupted JSON")

        service_id = self.context.get("service_id")
        services = self.application.services

        yield services.set_service_networks(service_id, networks)

        raise a.Redirect("service",
                         message="Service has been updated",
                         service_id=service_id)


class ServicesController(a.AdminController):
    @coroutine
    def get(self):

        services_data = self.application.services
        services = yield services_data.list_all_services("external")

        result = {
            "services": services.keys()
        }

        raise a.Return(result)

    def render(self, data):
        return [
            a.breadcrumbs([], "Services"),
            a.links("Services", links=[
                a.link("service", service_id, icon="wrench", service_id=service_id) for service_id in data["services"]
            ]),
            a.links("Navigate", [
                a.link("index", "Go back"),
                a.link("new_service", "New service", "plus")
            ])
        ]

    def scopes_read(self):
        return ["discovery_admin"]

    def scopes_write(self):
        return ["discovery_admin"]
