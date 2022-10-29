import sys
from env_variables import *
from send_request import send_request
import time


class KongService:
    _realm: str = ''
    services = KONG_SERVICES
    routes = KONG_ROUTES

    def __init__(self, realm: str):
        self._realm = realm
        for route in self.routes:
            route['hosts'].append("{realm}.{dashbboard_service_domain}.{environment}.{main_domain}".format(
                realm=realm, dashbboard_service_domain=DASHBOARD_SERVICE_DOMAIN, environment=ENVIRONMENT, main_domain=MAIN_DOMAIN))

    def check_kong(self):
        res_data = send_request(method="GET", url=KONG_API)
        if res_data.get("status_code") == 500:
            time.sleep(3)
            print(res_data["message"], " Reconnecting")
            return self.check_kong()
        else:
            return True

    def add_service(self, data):
        url = KONG_API + "/services"
        res_data = send_request("POST", url, data=data)

        if res_data["status_code"] != 201:
            print(res_data.get("message"))
            print(res_data["data"].get("errorMessage")
                  or res_data["data"].get("error"))
            sys.exit(100)
        return res_data

    def update_service(self, data):
        service_name = data.pop("name")
        url = KONG_API + \
            "/services/{service_name}".format(service_name=service_name)
        res_data = send_request("PATCH", url, data=data)

        if res_data["status_code"] != 200:
            print(res_data.get("message"))
            print(res_data["data"].get("errorMessage")
                  or res_data["data"].get("error"))
            sys.exit(100)

        return res_data

    def get_service(self, service_name):
        url = KONG_API + \
            "/services/{service_name}".format(service_name=service_name)
        res_data = send_request("GET", url)

        if res_data["status_code"] != 200 and res_data["status_code"] != 404:
            print(res_data.get("message"))
            print(res_data["data"].get("errorMessage")
                  or res_data["data"].get("error"))
            sys.exit(100)

        return res_data

    def get_services(self):
        url = KONG_API + "/services/"
        res_data = send_request("GET", url)

        if res_data["status_code"] != 200 and res_data["status_code"] != 404:
            print(res_data.get("message"))
            print(res_data["data"].get("errorMessage")
                  or res_data["data"].get("error"))
            sys.exit(100)

        return res_data

    def add_services(self):
        for service in self.services:
            service_name = service.get("name")

            service_res_data = self.get_service(service_name)
            service_data = service_res_data.get("data")

            if service_res_data.get("status_code") == 200:
                if (service_data.get("host") != service.get("host") or str(service_data.get("port")) != service.get("port")):
                    print('service_host_name or service_port not matched!')
                    print('Hostname in Kong: ' + service_data.get("host"))
                    print('Hostname in config: ' + service.get("host"))
                    print('Port in Kong: ' + str(service_data.get("port")))
                    print('Port in config: ' + service.get("port"))
                    self.update_service(service)
            elif service_res_data.get("status_code") == 404:
                print("ADDING SERVICE {service_name}".format(
                    service_name=service_name))
                self.add_service(service)
            else:
                print("ALL IS GOOD")

    def get_routes(self, kong_service):
        url = KONG_API + \
            "/services/{kong_service}/routes".format(kong_service=kong_service)
        res_data = send_request("GET", url)

        if res_data["status_code"] != 200:
            print(res_data.get("message"))
            print(res_data["data"].get("errorMessage")
                  or res_data["data"].get("error"))
            sys.exit(100)

        return res_data

    def add_route(self, kong_service_name, data):
        url = KONG_API + \
            "/services/{kong_service_name}/routes".format(
                kong_service_name=kong_service_name)
        res_data = send_request("POST", url, data=data)

        if res_data["status_code"] != 201:
            print(res_data.get("message"))
            print(res_data["data"].get("errorMessage")
                  or res_data["data"].get("error"))
            sys.exit(100)

        return res_data

    def update_route(self, kong_service_name, data, route_id):
        url = KONG_API + "/services/{kong_service_name}/routes/{route_id}".format(
            kong_service_name=kong_service_name, route_id=route_id)
        res_data = send_request("PUT", url, data=data)

        if res_data["status_code"] != 200:
            print(res_data.get("message"))
            print(res_data["data"].get("errorMessage")
                  or res_data["data"].get("error"))
            sys.exit(100)

        return res_data

    def get_route_hostnames(self, route_id):
        url = KONG_API + "/routes/{route_id}".format(route_id=route_id)
        res_data = send_request("GET", url)

        if res_data["status_code"] != 200:
            print(res_data.get("message"))
            print(res_data["data"].get("errorMessage")
                  or res_data["data"].get("error"))
            sys.exit(100)

        return res_data["data"].get('hosts')

    def get_route_hostname(self, route_id):
        hosts = self.get_route_hostnames(route_id)
        if hosts:
            return hosts[0]
        return None

    # what is redirect hostname used for
    def get_redirect_hostname(self, route_id):
        hostname = self.get_route_hostname(route_id)
        post_logout_redirect_uri = 'https://' + hostname

        try:
            env_item = get_env_variable("POST_LOGOUT_REDIRECT_URL")
            if (env_item == '/'):
                POST_LOGOUT_REDIRECT_URL = post_logout_redirect_uri
            else:
                POST_LOGOUT_REDIRECT_URL = env_item
        except:
            POST_LOGOUT_REDIRECT_URL = post_logout_redirect_uri

        return POST_LOGOUT_REDIRECT_URL

    def get_oidc_plugin_details(self, route_id):
        url = KONG_API + '/routes/{route_id}/plugins'.format(route_id=route_id)
        res_data = send_request("GET", url)

        if res_data["status_code"] != 200:
            print(res_data.get("message"))
            print(res_data["data"].get("errorMessage")
                  or res_data["data"].get("error"))
            sys.exit(100)

        for item in res_data['data'].get("data"):
            if (item['name'] == 'oidc'):
                return item
        return None

    def get_oidc_post_logout_redirect_uri(self, route_id):
        plugin_details = self.get_oidc_plugin_details(route_id)
        try:
            return plugin_details['config']['post_logout_redirect_uri']
        except:
            return None

    def get_oidc_discovery_url(self, route_id):
        plugin_details = self.get_oidc_plugin_details(route_id)
        try:
            return plugin_details['config']['discovery']
        except:
            return None

    def add_or_update_oidc_plugin(self, secret, discovery_url, route_id, service_id, put_method=False):
        hostname = self.get_route_hostname(route_id)
        base_hostname = 'www.' + ENVIRONMENT

        if EXTERNAL_FORWARDED_PORT:
            hostname = hostname + ':' + EXTERNAL_FORWARDED_PORT
            base_hostname = base_hostname + ':' + EXTERNAL_FORWARDED_PORT

        redirect_uri = 'https://{hostname}/redirect-uri'.format(
            hostname=hostname)

        POST_LOGOUT_REDIRECT_URL = self.get_redirect_hostname(route_id)

        data = {
            "name": "oidc",
            "route.id": route_id,
            "service.id": service_id,
            "config.realm": self._realm,
            "config.client_id": OIDC_CLIENT_ID,
            "config.client_secret": secret,
            "config.discovery": discovery_url,
            "config.redirect_uri": redirect_uri,
            "config.post_logout_redirect_uri": POST_LOGOUT_REDIRECT_URL,
        }
        url = KONG_API + "/plugins"
        if put_method:
            rec_details = self.get_oidc_plugin_details(route_id)
            rec_id = rec_details['id']
            url = KONG_API + "/plugins/" + rec_id
            res_data = send_request("PUT", url, data=data)
        else:
            res_data = send_request("POST", url, data=data)

        if res_data["status_code"] != 200 and res_data["status_code"] != 201 and res_data["status_code"] != 409:
            print(res_data.get("message"))
            print(res_data["data"].get("errorMessage")
                  or res_data["data"].get("error"))
            sys.exit(100)

        return res_data

    def add_routes_and_oidc_plugin(self, secret):
        for route in self.routes:
            kong_service_name = route.pop("service")

            routes_data = self.get_routes(
                kong_service_name).get("data").get("data")
            try:
                route_data = next(
                    route_data for route_data in routes_data if route_data["hosts"] == route.get("hosts"))
            except:
                route_data = None

            should_add_route = True
            if route_data:
                should_add_route = False
                if route.get("methods") == route_data.get("methods") and route.get("paths") == route_data.get("paths"):
                    route_id = route_data.get("id")
                    service_id = route_data.get("service").get("id")
                else:
                    print("UPDATING ROUTES FOR {kong_service_name}".format(
                        kong_service_name=kong_service_name))
                    res = self.update_route(kong_service_name, route,
                                            route_data.get("id"))
                    route_id = res["data"].get('id')
                    service_id = res["data"].get('service').get('id')

            if should_add_route:
                print("ADDING ROUTES FOR {kong_service_name}".format(
                    kong_service_name=kong_service_name))
                res = self.add_route(kong_service_name, route)
                route_id = res["data"].get('id')
                service_id = res["data"].get('service').get('id')

            discovery_url = DISCOVERY_URL.format(realm=self._realm)
            put_method = False

            # it return a url if a plugin is already installed
            db_post_logout_redirect_uri = self.get_oidc_post_logout_redirect_uri(
                route_id)
            db_oidc_discovery_url = self.get_oidc_discovery_url(route_id)
            if db_post_logout_redirect_uri and db_oidc_discovery_url:
                config_post_logout_redirect_uri = self.get_redirect_hostname(
                    route_id)
                if config_post_logout_redirect_uri != db_post_logout_redirect_uri:
                    print(config_post_logout_redirect_uri)
                    print(db_post_logout_redirect_uri)
                    put_method = True

                if db_oidc_discovery_url != discovery_url:
                    print("Discovery Url in the DB: {db_oidc_discovery_url}".format(
                        db_oidc_discovery_url=db_oidc_discovery_url))
                    print("Discovery Url : {discovery_url}".format(
                        discovery_url=discovery_url))
                    put_method = True

            # function call creating a plugin for realms in kong
            kong_response = self.add_or_update_oidc_plugin(
                secret, discovery_url, route_id, service_id, put_method)

            if kong_response.get("status_code") == 200:
                print("OIDC PLUGIN FOR {kong_service_name} IS UPDATED".format(
                    kong_service_name=kong_service_name))
            elif kong_response.get("status_code") == 201:
                print("OIDC PLUGIN FOR {kong_service_name} IS CREATED".format(
                    kong_service_name=kong_service_name))
            elif kong_response.get("status_code") == 409:
                print("OIDC PLUGIN FOR {kong_service_name} ALREADY EXISTS".format(
                    kong_service_name=kong_service_name))
