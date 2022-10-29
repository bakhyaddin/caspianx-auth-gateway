FROM quay.io/keycloak/keycloak:19.0.2

USER root

COPY ./themes/caspianx/ /opt/keycloak/themes/caspianx/

USER 1000

ENTRYPOINT ["/opt/keycloak/bin/kc.sh", "start-dev"]
