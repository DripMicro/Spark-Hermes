#!/bin/sh
# Build hermes-base at the pinned commit and tag family images FROM it. Run on the build host.
set -eu
COMMIT="${HERMES_COMMIT:?set HERMES_COMMIT}"
HERE="$(cd "$(dirname "$0")" && pwd)"
cp -r "$HERE/../runner" "$HERE/hermes-base/runner"
docker build --build-arg HERMES_COMMIT="$COMMIT" -t "hermes-base:${COMMIT}" -t hermes-base:pin "$HERE/hermes-base"
rm -rf "$HERE/hermes-base/runner"
docker image inspect hermes-base:pin --format 'hermes-base id={{.Id}}'
