#
# Modified from official python Dockerfile
#
# author(s): Albert (aki) Zhou
# origin: 11-05-2018
#

FROM ubuntu:18.04


# specify a version
ARG PACKAGE=kagami-2.0.0-py2-none-any.whl

# copy kagami installer
COPY dist/$PACKAGE .

# install python and dependencies and commonly used packages
RUN apt-get update
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
    && apt-get autoremove -y \
    && apt-get autoclean -y \
    && rm -rf /var/lib/apt/lists/* \
    && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python get-pip.py \
    && rm get-pip.py \
    && pip install --no-cache-dir wheel \
    && pip install --no-cache-dir $PACKAGE \
    && rm $PACKAGE \
