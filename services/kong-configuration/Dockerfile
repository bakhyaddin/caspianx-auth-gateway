FROM python:3.7

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

USER root

RUN mkdir /kong-configuration
WORKDIR /kong-configuration
COPY . /kong-configuration

RUN pip install --no-cache-dir -r /kong-configuration/requirements.txt \
  && chmod +x /kong-configuration/docker-entrypoint.sh

USER 1001

CMD ["/bin/sh", "/kong-configuration/docker-entrypoint.sh"]