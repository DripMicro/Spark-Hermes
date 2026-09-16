FROM hermes-ubuntu:pin
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        git \
        unzip \
        wget \
        curl \
        file \
        && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --no-cache-dir python-pptx
WORKDIR /task_file
COPY build_scripts/ /tmp/build_scripts/
RUN chmod +x /tmp/build_scripts/*.sh && \
    bash /tmp/build_scripts/generate_pptx.sh && \
    rm -rf /tmp/build_scripts
COPY task_file/ /task_file/
USER root
RUN mkdir -p /task_file && chown -R 1000:1000 /task_file
USER 1000:1000
WORKDIR /task_file
