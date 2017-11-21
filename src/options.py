
from common.options import define

# Main

define("host",
       default="http://localhost:9502",
       help="Public hostname of this service",
       type=str)

define("listen",
       default="port:9502",
       help="Socket to listen. Could be a port number (port:N), or a unix domain socket (unix:PATH)",
       type=str)

define("name",
       default="discovery",
       help="Service short name. User to discover by discovery service.",
       type=str)

# Discover services

define("discover_services_host",
       default="127.0.0.1",
       help="Location of service discovery database (redis).",
       group="discover_services",
       type=str)

define("discover_services_port",
       default=6379,
       help="Port of service discovery database (redis).",
       group="discover_services",
       type=int)

define("discover_services_db",
       default=15,
       help="Database of service discovery database (redis).",
       group="discover_services",
       type=int)

define("discover_services_max_connections",
       default=500,
       help="Maximum connections to the service discovery database (connection pool).",
       group="discover_services",
       type=int)

# Discovery services init file

# If the service is started up with no records at all, the service will fill up the database with records from the
# file provided. Please note that this will only happen once.

define("services_init_file",
       default="../dev/discovery-services.json",
       help="JSON file with default services locations (used to initialize an empty database)",
       group="discovery",
       type=str)
