#
# Modified from official python Dockerfile
#
# author(s): Albert (aki) Zhou
# origin: 11-05-2018
#

FROM python:2.7.15-slim

# envs
ARG TIMEZONE=GB
ARG PACKAGE=kagami-2.2.7-py2-none-any.whl

# copy kagami installer
COPY entrypoint.sh /usr/local/bin/
COPY $PACKAGE .

# install python and dependencies and commonly used packages
RUN ln -snf /usr/share/zoneinfo/$TIMEZONE /etc/localtime && echo $TIMEZONE > /etc/timezone \
    && apt-get update && apt-get install -y --no-install-recommends \
	   r-base \
	   r-base-dev \
    && pip install --upgrade --no-cache-dir pip \
    && pip install --no-cache-dir wheel \
    && pip install --no-cache-dir $PACKAGE && rm $PACKAGE \
    && pip install --no-cache-dir pytest-profiling pytest-cov \
    && apt-get autoremove -y && apt-get autoclean -y \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && rm -rf /var/lib/apt/lists/* \
    && chmod a+x /usr/local/bin/entrypoint.sh && ln -s /usr/local/bin/entrypoint.sh / \
    && mkdir -p /home

# prevent attach and exec bash (optional)
ENV ENV=/root/.shinit
RUN echo "exit" > /root/.shinit && echo "exit" > /root/.bashrc && echo "exit" > /etc/bash.bashrc

# add Tini
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

# set entry
WORKDIR /home
ENTRYPOINT ["/tini", "--", "entrypoint.sh"]
