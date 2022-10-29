import os


def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)


def load_variable_from_secret_file(env_var):
    try:
        file_path = os.environ[env_var]
        with open(file_path) as f:
            var_contents = f.read().strip()
        return var_contents
    except KeyError:
        message = "Expected secret variable '{}' not set.".format(env_var)
        raise Exception(message)


ENVIRONMENT = get_env_variable("ENVIRONMENT")

# Required for integration with keycloak master tenant to create new sub tenants.
IAM_SERVICE = get_env_variable("IAM_SERVICE")
IAM_ADMIN_CLIENT_ID = get_env_variable("IAM_ADMIN_CLIENT_ID")
IAM_ADMIN_USERNAME = get_env_variable("IAM_ADMIN_USERNAME")
IAM_ADMIN_PASSWORD = get_env_variable("IAM_ADMIN_PASSWORD")
OIDC_CLIENT_ID = get_env_variable("OIDC_CLIENT_ID")


DISCOVERY_URL = get_env_variable("DISCOVERY_URL")
KONG_API = get_env_variable("KONG_API")
DASHBOARD_SERVICE_DOMAIN = get_env_variable("DASHBOARD_SERVICE_DOMAIN")
MAIN_DOMAIN = get_env_variable("MAIN_DOMAIN")


USER_MANAGEMENT_SERVICE = get_env_variable("USER_MANAGEMENT_SERVICE")
USER_MANAGEMENT_SERVICE_PORT = get_env_variable(
    "USER_MANAGEMENT_SERVICE_PORT")

METHODS = ["POST", "PUT", "GET", "OPTIONS", "DELETE", "PATCH"]
USER_MANAGEMENT_PATHS = [
    "/api/user-management", "/redirect-uri"]

KONG_SERVICES = [
    {
        "host": USER_MANAGEMENT_SERVICE,
        "protocol": "http",
        "name": USER_MANAGEMENT_SERVICE,
        "port": USER_MANAGEMENT_SERVICE_PORT,
    }
]

KONG_ROUTES = [
    {
        "service": USER_MANAGEMENT_SERVICE,
        "hosts": [],
        "paths": USER_MANAGEMENT_PATHS,
        "methods": METHODS
    }
]

try:
    # EXTERNAL_FORWARDED_PORT env variable used in all configuration settings when external port is different
    # e.g when system is accessible at https://master1.dev.midentity.one:10192 but internally it listens on 443
    EXTERNAL_FORWARDED_PORT = get_env_variable("EXTERNAL_FORWARDED_PORT")
except:
    EXTERNAL_FORWARDED_PORT = None
