FROM python:3.6
MAINTAINER Manuel Gómez <targen@gmail.com>

# Note: This project doesn't use the official Django image because it adds
# build arguments that direct pip to a caching proxy.  This speeds up builds
# dramatically on slow connections when paired with a local PyPI cache.  See
# <https://github.com/mgomezch/local_services> for instructions on how to
# run a local devpi PyPI caching proxy within Docker.

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
  gcc \
  gettext \
  postgresql-client libpq-dev \
  sqlite3 \
  --no-install-recommends && rm -rf /var/lib/apt/lists/*

ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["./services/web/docker-entrypoint.sh"]
CMD ["development"]

EXPOSE 80

COPY . /usr/src/app
RUN mkdocs build
