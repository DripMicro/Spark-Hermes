#!/bin/sh
# Build the agent images at the pinned commit. Run on the build host.
#   hermes-base:pin    python:3.12-slim + hermes  (families that ship their own fixtures)
#   hermes-ubuntu:pin  ubuntu:22.04 + hermes      (image-defined tasks: family terminal_task builds FROM it)
set -eu
COMMIT="${HERMES_COMMIT:?set HERMES_COMMIT}"
HERE="$(cd "$(dirname "$0")" && pwd)"
for base in hermes-base hermes-ubuntu; do
  rm -rf "$HERE/$base/runner"
  cp -r "$HERE/../runner" "$HERE/$base/runner"
  cp -r "$HERE/../../predicates" "$HERE/$base/runner/predicates"  # the runner imports the same predicates the validator grades with
  rm -rf "$HERE/$base/runner/__pycache__" "$HERE/$base/runner/predicates/__pycache__"
  docker build --build-arg HERMES_COMMIT="$COMMIT" -t "$base:${COMMIT}" -t "$base:pin" "$HERE/$base"
  rm -rf "$HERE/$base/runner"
  docker image inspect "$base:pin" --format "$base id={{.Id}}"
done
