FROM hermes-ubuntu:pin
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        fonts-liberation \
        zip \
        unzip \
        curl \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --no-cache-dir \
        python-docx==0.8.11 \
        Pillow==10.2.0 \
        cairosvg==2.7.1 \
        reportlab==4.1.0
WORKDIR /task_file
COPY build_scripts/ /tmp/build_scripts/
RUN chmod +x /tmp/build_scripts/*.sh /tmp/build_scripts/*.py 2>/dev/null; \
    python3 /tmp/build_scripts/generate_fixtures.py && \
    rm -rf /tmp/build_scripts
COPY task_file/ /task_file/
USER root
RUN mkdir -p /task_file && chown -R 1000:1000 /task_file
USER 1000:1000
WORKDIR /task_file
