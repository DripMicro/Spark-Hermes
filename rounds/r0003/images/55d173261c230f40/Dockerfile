FROM hermes-ubuntu:pin
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        git \
        jq \
        && rm -rf /var/lib/apt/lists/*
WORKDIR /task_file
COPY task_file/ /task_file/
COPY build_scripts/ /tmp/FACET-Terminal-build-scripts/
USER root
RUN mkdir -p /task_file && chown -R 1000:1000 /task_file
USER 1000:1000
WORKDIR /task_file
