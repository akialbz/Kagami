#
# Modified from official python Dockerfile
#
# author(s): Albert (aki) Zhou
# origin: 11-05-2018
#

FROM debian:stretch-slim

# envs
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_COLLATE=C \
    LC_CTYPE=C \
    LC_MESSAGES=C \
    LC_MONETARY=C \
    LC_NUMERIC=C \
    LC_TIME=C \
    LC_ALL=C \
    PYTHONDONTWRITEBYTECODE=1

ARG TIMEZONE=GB
ARG PACKAGE=kagami-2.0.0-py2-none-any.whl

# copy kagami installer
COPY $PACKAGE .

# install python and dependencies and commonly used packages
RUN ln -snf /usr/share/zoneinfo/$TIMEZONE /etc/localtime \
    && echo $TIMEZONE > /etc/timezone \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
       netbase \
       dpkg-dev \
       gcc \
       libbz2-dev \
       libc6-dev \
       libdb-dev \
       libgdbm-dev \
       libncursesw5-dev \
       libreadline-dev \
       libsqlite3-dev \
       libssl-dev \
       make \
       tk-dev \
       wget \
       xz-utils \
       zlib1g-dev \
       curl \
       python \
       python-dev \
       r-base \
       r-base-dev \
    && apt-get autoremove -y \
    && apt-get autoclean -y \
    && rm -rf /var/lib/apt/lists/* \
    && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python get-pip.py \
    && rm get-pip.py \
    && pip install --no-cache-dir wheel \
    && pip install --no-cache-dir $PACKAGE \
    && pip install --no-cache-dir pytest-profiling \
    && pip install --no-cache-dir pytest-cov \
    && rm $PACKAGE \
    && mkdir -p /home

# set entry
WORKDIR /home
ENTRYPOINT ["python"]
