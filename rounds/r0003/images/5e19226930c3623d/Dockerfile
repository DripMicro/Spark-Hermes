FROM hermes-ubuntu:pin
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip python3-venv git jq && \
    rm -rf /var/lib/apt/lists/*
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
WORKDIR /task_file
# Copy build scripts and execute fixture generators
COPY build_scripts/ /build_scripts/
RUN python3 /build_scripts/generate_fixtures.py && \
    rm -rf /build_scripts
COPY task_file/ /task_file/
USER root
RUN mkdir -p /task_file && chown -R 1000:1000 /task_file
USER 1000:1000
WORKDIR /task_file
