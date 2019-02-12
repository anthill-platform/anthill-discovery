import anthill.common.admin as a

import ujson

from . model.discovery import ServiceNotFound, DiscoveryModel


class NewServiceController(a.AdminController):
    async def create(self, service_id, networks):

        services = self.application.services

        try:
            networks = ujson.loads(networks)
        except (KeyError, ValueError):
            raise a.ActionError("Corrupted JSON")

        await services.set_service_networks(service_id, networks)

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
                a.link("@back", "Go back", icon="chevron-left")
            ])
        ]

    def access_scopes(self):
        return ["discovery_admin"]


class CloneServiceController(a.AdminController):
    async def clone(self, service_id, networks):

        services = self.application.services

        try:
            networks = ujson.loads(networks)
        except (KeyError, ValueError):
            raise a.ActionError("Corrupted JSON")

        await services.set_service_networks(service_id, networks)

        raise a.Redirect(
            "service",
            message="New service has been cloned",
            service_id=service_id)

    async def get(self, service_id):

        services = self.application.services

        try:
            networks = await services.list_service_networks(service_id)
        except ServiceNotFound:
            raise a.ActionError("No such service: " + service_id)

        result = {
            "networks": networks
        }

        return result

    def render(self, data):
        return [
            a.breadcrumbs([
                a.link("services", "Services")
            ], "Clone service"),
            a.form("Clone service '{0}'".format(self.context.get("service_id")), fields={
                "service_id": a.field("Service ID", "text", "danger", "non-empty"),
                "networks": a.field(
                    "Service networks", "kv", "primary", "non-empty",
                    values={network: network for network in DiscoveryModel.NETWORKS}),
            }, methods={
                "clone": a.method("Clone", "primary")
            }, data=data),
            a.links("Navigate", [
                a.link("@back", "Go back", icon="chevron-left")
            ])
        ]

    def access_scopes(self):
        return ["discovery_admin"]


class RootAdminController(a.AdminController):
    def render(self, data):
        return [
            a.links("Discovery service", [
                a.link("services", "Edit services", icon="wrench")
            ])
        ]

    def access_scopes(self):
        return ["discovery_admin"]


class ServiceController(a.AdminController):
    # noinspection PyUnusedLocal
    async def delete(self, **ignored):
        service_id = self.context.get("service_id")
        services = self.application.services

        await services.delete_service(service_id)

        raise a.Redirect("services", message="Service has been deleted")

    async def get(self, service_id):

        services = self.application.services

        try:
            networks = await services.list_service_networks(service_id)
        except ServiceNotFound:
            raise a.ActionError("No such service: " + service_id)

        result = {
            "networks": networks
        }

        return result

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
                a.link("services", "Go back", icon="chevron-left"),
                a.link("new_service", "New service", "plus"),
                a.link("clone_service", "Clone service", "clone", service_id=self.context.get("service_id"))
            ])
        ]

    def access_scopes(self):
        return ["discovery_admin"]

    async def update(self, networks):

        try:
            networks = ujson.loads(networks)
        except (KeyError, ValueError):
            raise a.ActionError("Corrupted JSON")

        service_id = self.context.get("service_id")
        services = self.application.services

        await services.set_service_networks(service_id, networks)

        raise a.Redirect("service",
                         message="Service has been updated",
                         service_id=service_id)


class ServicesController(a.AdminController):
    async def get(self):

        services_data = self.application.services
        services = await services_data.list_all_services("external")

        result = {
            "services": list(services.keys())
        }

        return result

    def render(self, data):
        return [
            a.breadcrumbs([], "Services"),
            a.links("Services", links=[
                a.link("service", service_id, icon="wrench", service_id=service_id) for service_id in data["services"]
            ]),
            a.links("Navigate", [
                a.link("index", "Go back", icon="chevron-left"),
                a.link("new_service", "New service", "plus")
            ])
        ]

    def access_scopes(self):
        return ["discovery_admin"]
