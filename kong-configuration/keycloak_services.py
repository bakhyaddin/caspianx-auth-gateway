import sys
import json
import time
from send_request import send_request
from env_variables import *


class KeycloakService:
    _realm: str = ''
    master_access_token: str = ''

    def __init__(self, realm: str):
        self._realm = realm
        self.check_keycloak()
        self.master_access_token = self.login_master()

    def check_keycloak(self):
        data = send_request(method="GET", url=IAM_SERVICE,
                            service_type="Keycloak")
        if data.get("status_code") == 500:
            time.sleep(3)
            print(data["message"], " Reconnecting Keycloak")
            return self.check_keycloak()
        else:
            return True

    # always make request with the MASTER tenant's token
    def login_master(self):
        req_data = {
            "client_id": IAM_ADMIN_CLIENT_ID,
            "username": IAM_ADMIN_USERNAME,
            "password": IAM_ADMIN_PASSWORD,
            "grant_type": "password"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        url = "{iam_service}/realms/master/protocol/openid-connect/token".format(
            iam_service=IAM_SERVICE)

        data = send_request(method="POST", url=url, headers=headers,
                            data=req_data, service_type="Keycloak")

        if data["status_code"] != 200:
            print(data.get("message"),
                  " Could not login to keycloak with master realm")
            print(data["data"].get("error"))
            sys.exit(100)

        return data.get("data").get("access_token")

    def create_realm(self):
        req_data = {
            "id": self._realm,
            "realm": self._realm,
            "enabled": True
        }

        headers = {'Authorization': 'Bearer {token}'.format(
            token=self.master_access_token), 'Content-Type': 'application/json'}

        url = "{iam_service}/admin/realms".format(iam_service=IAM_SERVICE)

        data = send_request("POST", url, headers=headers,
                            data=json.dumps(req_data), service_type="Keycloak")

        if data["status_code"] != 201:
            print(data.get("message"))
            print("Could not create realm '{realm}'".format(realm=self._realm), data["data"].get(
                "errorMessage") or data["data"].get("error"))
            sys.exit(100)

    # create dashboard kong
    def create_dashboard_client(self):
        req_data = {
            "clientId": OIDC_CLIENT_ID,
            "name": OIDC_CLIENT_ID,
            "clientAuthenticatorType": "client-secret",
            "redirectUris": [
                "https://{realm}.{dashbboard_service_domain}.{environment}.{main_domain}/*".format(
                    realm=self._realm, dashbboard_service_domain=DASHBOARD_SERVICE_DOMAIN, environment=ENVIRONMENT, main_domain=MAIN_DOMAIN),
            ],
            "bearerOnly": False,
            "serviceAccountsEnabled": True,
            "publicClient": False,
            "protocol": "openid-connect",
            "authorizationServicesEnabled": True,
        }

        headers = {'Authorization': 'Bearer {token}'.format(
            token=self.master_access_token), 'Content-Type': 'application/json'}

        url = "{iam_service}/admin/realms/{realm}/clients".format(
            iam_service=IAM_SERVICE, realm=self._realm)

        data = send_request("POST", url, headers=headers,
                            data=json.dumps(req_data), service_type="Keycloak")

        if data["status_code"] != 201 and data["status_code"] != 409:
            print(data.get("message"))
            print("Could not create OIDC(Dashboard) client ", data["data"].get(
                "errorMessage") or data["data"].get("error"))
            sys.exit(100)

        if data.get("redirectUris") != req_data.get("redirectUris"):
            print("UPDATING CLIENT {client_name}".format(
                client_name=OIDC_CLIENT_ID))
            return self.update_dashboard_client(req_data=req_data)
        return data

    def update_dashboard_client(self, req_data):
        oidc_client_id = self.get_dashboard_client_id()

        headers = {'Authorization': 'Bearer {token}'.format(
            token=self.master_access_token), 'Content-Type': 'application/json'}
        url = "{iam_service}/admin/realms/{realm}/clients/{oidc_client_id}".format(
            iam_service=IAM_SERVICE, realm=self._realm, oidc_client_id=oidc_client_id)

        data = send_request("PUT", url, headers=headers,
                            data=json.dumps(req_data), service_type="Keycloak")

        if data["status_code"] != 204:
            print(data.get("message"))
            print("Could not Update OIDC client ", data["data"].get(
                "errorMessage") or data["data"].get("error"))
            sys.exit(100)

        return data

    # get dashboard client secret
    def get_dashboard_client_secret(self):
        oidc_client_id = self.get_dashboard_client_id()

        headers = {'Authorization': 'Bearer {token}'.format(
            token=self.master_access_token)}
        url = "{iam_service}/admin/realms/{realm}/clients/{oidc_client_id}/client-secret".format(
            iam_service=IAM_SERVICE, realm=self._realm, oidc_client_id=oidc_client_id)

        data = send_request("GET", url, headers=headers,
                            service_type="Keycloak")

        if data["status_code"] != 200:
            print(data.get("message"))
            print("Could not get OIDC(Dashboard) client secret", data["data"].get(
                "errorMessage") or data["data"].get("error"))
            sys.exit(100)

        return data.get("data").get("value")

    # fetch dashboard client id
    def get_dashboard_client_id(self):
        headers = {'Authorization': 'Bearer {token}'.format(
            token=self.master_access_token)}
        url = "{iam_service}/admin/realms/{realm}/clients?clientId={oidc_client_id}".format(
            iam_service=IAM_SERVICE, realm=self._realm, oidc_client_id=OIDC_CLIENT_ID)

        data = send_request("GET", url, headers=headers,
                            service_type="Keycloak")

        if data["status_code"] != 200:
            print(data.get("message"))
            print("Could not get clients", data["data"].get(
                "errorMessage") or data["data"].get("error"))
            sys.exit(100)

        return data.get("data")[0].get("id")
