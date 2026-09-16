#!/bin/sh
# Build the agent image at the pinned commit, on the build host (the worker, whose Docker also serves derivation):
#   hermes-ubuntu:pin  ubuntu:22.04 + hermes-agent + the runner — every task image composes onto it
set -eu
COMMIT="${HERMES_COMMIT:?set HERMES_COMMIT}"
HERE="$(cd "$(dirname "$0")" && pwd)"
base=hermes-ubuntu
rm -rf "$HERE/$base/runner"
cp -r "$HERE/../runner" "$HERE/$base/runner"
# A stale runner/predicates/ in the source tree (an old checkout, an rsync that could not delete) would make
# `cp -r` nest the package inside it and leave the runner with a bare directory — a namespace package with no
# `evaluate`, and a grader that cannot grade. Remove whatever is there first, and prove the import after the build.
rm -rf "$HERE/$base/runner/predicates"
cp -r "$HERE/../../predicates" "$HERE/$base/runner/predicates"  # the runner imports the same predicates the validator grades with
find "$HERE/$base/runner" -name __pycache__ -type d -exec rm -rf {} +
docker build --build-arg HERMES_COMMIT="$COMMIT" -t "$base:${COMMIT}" -t "$base:pin" "$HERE/$base"
rm -rf "$HERE/$base/runner"
docker run --rm "$base:pin" /opt/hermes/.venv/bin/python -c \
  "import sys; sys.path.insert(0, '/runner'); import predicates; assert predicates.__file__ and predicates.evaluate; print('runner predicates ok')"
docker image inspect "$base:pin" --format "$base id={{.Id}}"
