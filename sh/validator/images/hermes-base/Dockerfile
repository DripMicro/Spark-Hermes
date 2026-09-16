# hermes-base: unmodified hermes-agent at a pinned commit, on the Python range it declares
# (>=3.11,<3.14). Every family image builds FROM this so the agent layer is identical across families
# (spec §5.1 topology a). No family sources, no solutions, no checks ever enter an image.
FROM python:3.12-slim-bookworm
ARG HERMES_COMMIT
RUN test -n "$HERMES_COMMIT"
ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential dash bash coreutils procps ripgrep \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv
RUN mkdir -p /opt/hermes && cd /opt/hermes && git init -q \
    && git fetch -q --depth 1 https://github.com/NousResearch/hermes-agent "$HERMES_COMMIT" \
    && git checkout -q FETCH_HEAD && rm -rf .git
WORKDIR /opt/hermes
# .python-version in the repo says 3.11, which would make uv download a managed interpreter under
# /root -- unreadable by uid 1000 at run time ("Could not find platform independent libraries").
# Sync against the image's system interpreter instead; 3.12 is inside Hermes' declared range.
ENV UV_PYTHON_DOWNLOADS=never
RUN uv sync --frozen --no-dev --python /usr/local/bin/python3 2>&1 | tail -5 \
    && readlink -f /opt/hermes/.venv/bin/python | grep -q /usr/local/bin/python3
RUN useradd -u 1000 -m -d /home/hermes hermes
COPY runner/ /runner/
ENV PATH=/opt/hermes/.venv/bin:$PATH HERMES_HOME=/home/hermes HOME=/home/hermes
LABEL org.spark-hermes.hermes-commit="$HERMES_COMMIT"
USER 1000:1000
