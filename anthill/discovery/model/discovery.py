
from anthill.common import keyvalue

from anthill.common.options import options
from anthill.common.model import Model
from anthill.common.validate import validate, validate_value, ValidationError

import ujson
import logging


class DiscoveryError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return str(self.code) + ": " + str(self.message)


class DiscoveryModel(Model):

    INTERNAL = "internal"
    EXTERNAL = "external"
    BROKER = "broker"

    NETWORKS = [INTERNAL, EXTERNAL, BROKER]

    def __init__(self, application):
        self.application = application

        self.kv = keyvalue.KeyValueStorage(
            host=options.discover_services_host,
            port=options.discover_services_port,
            db=options.discover_services_db)

    async def started(self, application):
        services_init_file = options.services_init_file

        if services_init_file:
            is_empty = await self.is_empty()

            if is_empty:
                logging.info("Discovery records database is empty, initializing from {0}".format(services_init_file))

            try:
                with open(services_init_file, "r") as f:
                    data = ujson.load(f)
            except IOError as e:
                raise DiscoveryError(500, "Failed to load services init file: " + str(e))
            else:
                if not is_empty:
                    data = await self.get_unloaded_data(data)
                await self.setup_services(data)

    @validate(data="json_dict")
    async def get_unloaded_data(self, data):
        async with self.kv.acquire() as db:
            _data = {"services": {}}
            db_keys = await db.keys("*")
            try:
                data_keys = data["services"].keys()
            except KeyError:
                raise DiscoveryError(400, "Init file has no 'services' section defined.")
            else:
                if len(data_keys) > len(db_keys):
                    for key in data_keys:
                        if key not in db_keys:
                            _data["services"][key] = data["services"][key]
            return _data

    @validate(data="json_dict")
    async def setup_services(self, data):
        try:
            services = validate_value(data["services"], "json_dict")
        except (KeyError, ValueError):
            raise DiscoveryError(400, "Init file has no 'services' section defined.")

        for service_id, info in services.items():
            try:
                networks = validate_value(info, "json_dict_of_strings")
            except ValidationError as e:
                raise DiscoveryError(400, e.message)

            await self.set_service_networks(service_id, networks)

    async def is_empty(self):
        async with self.kv.acquire() as db:
            keys = await db.keys("*")
            return len(keys) == 0

    async def delete_service(self, service_id):
        async with self.kv.acquire() as db:
            await db.delete(service_id)

    async def delete_service_network(self, service_id, network):
        async with self.kv.acquire() as db:
            await db.hdel(service_id, network)

    async def list_all_services(self, network):
        async with self.kv.acquire() as db:
            keys = await db.keys("*")
            services = {}
            for key in keys:
                location = await db.hget(key, network)
                services[key] = location
        return services

    # noinspection PyUnusedLocal
    async def get_service(self, service_id, network, **ignored):
        async with self.kv.acquire() as db:
            service = await db.hget(service_id, network)
            if not service:
                raise ServiceNotFound(service_id)
        return service.decode("utf-8")

    async def list_service_networks(self, service_id):
        async with self.kv.acquire() as db:
            services = await db.hgetall(service_id)
            if not services:
                raise ServiceNotFound(service_id)
            return services or {}

    async def list_services(self, service_ids, network):
        async with self.kv.acquire() as db:
            service_locations = {}

            for service_id in service_ids:
                service = await db.hget(service_id, network)

                if service is None or len(service) == 0:
                    raise ServiceNotFound(service_id)
                else:
                    service_locations[service_id] = service

        return service_locations

    async def set_service(self, service_id, service_location, network):
        async with self.kv.acquire() as db:
            await db.hset(service_id, network, service_location)
            logging.info("Updated service '{0}' location to {1}/{2}".format(
                service_id, network, str(service_location)))

    async def set_service_networks(self, service_id, networks):
        async with self.kv.acquire() as db:
            await db.delete(service_id)

            for network, service_location in networks.items():
                await db.hset(service_id, network, service_location)

            logging.info("Updated service '{0}' location to {1}".format(service_id, str(networks)))


class ServiceNotFound(Exception):
    def __init__(self, service_id):
        self.service_id = service_id
