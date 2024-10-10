#/bin/bash
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    export DOCKER_UID="$(id -u)"
    export DOCKER_GID="$(id -g)"
    export DOCKER_UID_GID="$(id -u):$(id -g)"
fi
cd "$(dirname "$0")"
docker compose up
