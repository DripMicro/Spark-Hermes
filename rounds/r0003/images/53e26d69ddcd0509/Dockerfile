FROM hermes-ubuntu:pin
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        git \
        pandoc \
        libreoffice-writer \
        curl \
        jq && \
    rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir python-docx
WORKDIR /task_file
COPY task_file/ /task_file/
COPY build_scripts/ /build_scripts/
RUN chmod +x /build_scripts/*.sh && \
    python3 /build_scripts/generate_draft_docx.py && \
    /build_scripts/generate_chart_image.sh
USER root
RUN mkdir -p /task_file && chown -R 1000:1000 /task_file
USER 1000:1000
WORKDIR /task_file
