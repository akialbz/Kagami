#
# Modified from official python Dockerfile
#
# author(s): Albert (aki) Zhou
# origin: 11-05-2018
#

FROM python:2.7.15-slim

# envs
ARG TIMEZONE=GB
ARG PACKAGE=kagami

# copy kagami installer
COPY entrypoint.sh /usr/local/bin/

# install python and dependencies and commonly used packages
RUN ln -snf /usr/share/zoneinfo/$TIMEZONE /etc/localtime && echo $TIMEZONE > /etc/timezone \
    # install R
    && apt-get update && apt-get install -y --no-install-recommends \
	   r-base \
	   r-base-dev \
	# install kagami and dependencies
    && pip install --upgrade --no-cache-dir pip \
    && pip install --no-cache-dir \
       wheel \
       numpy \
       scipy \
       scikit-learn \
       statsmodels \
       pandas \
       networkx \
       matplotlib \
       plotly \
       bokeh \
       numba \
       pytest==3.10.1 \
       pytest-profiling \
       pytest-cov \
       rpy2==2.8.6 \
       $PACKAGE \
    # clean
    && apt-get purge -y \
       gcc \
       make \
       libc6-dev \
       r-base-dev \
    && find /usr/local -depth \
       \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
       -exec rm -rf '{}' + \
    && apt-get autoremove -y && apt-get autoclean -y \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && rm -rf /var/lib/apt/lists/* \
    # set entry point and work dir
    && chmod a+x /usr/local/bin/entrypoint.sh && ln -s /usr/local/bin/entrypoint.sh / \
    && mkdir -p /home

# prevent attach and exec bash (optional)
ENV ENV=/root/.shinit
RUN echo "exit" > /root/.shinit && echo "exit" > /root/.bashrc && echo "exit" > /etc/bash.bashrc

# set entry
WORKDIR /home
ENTRYPOINT ["entrypoint.sh"]
