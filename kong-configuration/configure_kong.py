import sys

from kong_services import KongService
from keycloak_services import KeycloakService

keycloak_service = KeycloakService('testdashboard')
keycloak_service.create_realm()
keycloak_service.create_dashboard_client()
dashboard_client_secret = keycloak_service.get_dashboard_client_secret()

kong_service = KongService('testdashboard')
kong_service.check_kong()
kong_service.add_services()
kong_service.add_routes_and_oidc_plugin(secret=dashboard_client_secret)

sys.exit(0)
