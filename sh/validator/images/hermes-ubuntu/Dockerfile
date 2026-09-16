# hermes-ubuntu: unmodified hermes-agent at the pinned commit on ubuntu:22.04 — the base every FACET task
# environment starts from. A task image is this plus the task's own Dockerfile body, so the agent layer is
# identical across tasks and the task layer is exactly what the dataset ships (spec §5.1 topology a).
# No family sources, no solutions, no checks ever enter an image.
FROM ubuntu:22.04
ARG HERMES_COMMIT
RUN test -n "$HERMES_COMMIT"
ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential dash bash coreutils procps ripgrep \
      python3 python3-pip python3-venv jq \
    && rm -rf /var/lib/apt/lists/*
# Hermes needs Python >=3.11 and jammy ships 3.10: a uv-managed CPython 3.12 in a world-readable prefix
# (under /root it is unreadable by uid 1000 at run time — the mistake hermes-base documents).
RUN curl -LsSf https://astral.sh/uv/0.9.7/install.sh | env UV_INSTALL_DIR=/usr/local/bin INSTALLER_NO_MODIFY_PATH=1 sh
ENV UV_PYTHON_INSTALL_DIR=/opt/uvpython UV_PYTHON_PREFERENCE=only-managed
RUN uv python install 3.12 && chmod -R a+rX /opt/uvpython
RUN mkdir -p /opt/hermes && cd /opt/hermes && git init -q \
    && git fetch -q --depth 1 https://github.com/NousResearch/hermes-agent "$HERMES_COMMIT" \
    && git checkout -q FETCH_HEAD && rm -rf .git
WORKDIR /opt/hermes
RUN uv sync --frozen --no-dev --python 3.12 2>&1 | tail -5 && /opt/hermes/.venv/bin/python -c "import sys; assert sys.version_info[:2] == (3, 12)"
# The tasks' verifiers are pytest files run on the system interpreter, which the task layer may extend.
RUN python3 -m pip install --no-cache-dir pytest==8.3.5
RUN useradd -u 1000 -m -d /home/hermes hermes
COPY runner/ /runner/
ENV PATH=/opt/hermes/.venv/bin:$PATH HERMES_HOME=/home/hermes HOME=/home/hermes
LABEL org.spark-hermes.hermes-commit="$HERMES_COMMIT"
