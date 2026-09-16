#!/bin/sh
# Build the agent image at the pinned commit, on the build host (the worker, whose Docker also serves derivation):
#   hermes-ubuntu:pin  ubuntu:22.04 + hermes-agent + the runner — every task image composes onto it
set -eu
COMMIT="${HERMES_COMMIT:?set HERMES_COMMIT}"
HERE="$(cd "$(dirname "$0")" && pwd)"
base=hermes-ubuntu
rm -rf "$HERE/$base/runner"
cp -r "$HERE/../runner" "$HERE/$base/runner"
cp -r "$HERE/../../predicates" "$HERE/$base/runner/predicates"  # the runner imports the same predicates the validator grades with
rm -rf "$HERE/$base/runner/__pycache__" "$HERE/$base/runner/predicates/__pycache__"
docker build --build-arg HERMES_COMMIT="$COMMIT" -t "$base:${COMMIT}" -t "$base:pin" "$HERE/$base"
rm -rf "$HERE/$base/runner"
docker image inspect "$base:pin" --format "$base id={{.Id}}"
