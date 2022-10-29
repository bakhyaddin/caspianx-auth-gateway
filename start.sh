docker-compose up -d postgres
docker-compose run --rm kong kong migrations bootstrap
docker-compose run --rm kong kong migrations up
docker-compose up -d kong
docker-compose up -d keycloak
docker-compose up -d kong-configuration
docker-compose up -d user-management
docker-compose ps
curl -s http://localhost:8001 | jq .plugins.available_on_server.oidc