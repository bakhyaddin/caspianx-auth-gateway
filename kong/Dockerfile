FROM kong:2.8.0

USER root

RUN apk add --update --no-cache --virtual .build-deps \
   build-base \
   openssl-dev \
   unzip \
&& luarocks install luaossl \
&& luarocks install --pin lua-resty-jwt \
&& apk del .build-deps 

# COPY docker-entrypoint.sh /docker-entrypoint.sh
# COPY nginx-kong.conf /usr/local/kong/nginx-kong-modified.conf
COPY oidc-plugin/ /usr/local/share/lua/5.1/kong/plugins/oidc/
COPY lua-resty-openidc/openidc.lua /usr/local/share/lua/5.1/resty/openidc.lua

# RUN chmod 755 /docker-entrypoint.sh

# ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 8000 8443 8001 8444

STOPSIGNAL SIGQUIT

CMD ["kong", "docker-start"]
