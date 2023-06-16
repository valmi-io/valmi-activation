#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

if [[ "${TRACE-0}" == "1" ]]; then
    set -o xtrace
fi

if [[ "${1-}" =~ ^-*h(elp)?$ ]]; then
    echo 'Usage: 
    ./run.sh [ACTION] [STAGE]
    ./run.sh prod/dev 
    
    Script to manage valmi-activaiton services.
    '
    exit
fi

src_dir="$(cd "$(dirname "$0")"; pwd -P)"

#Apply all environment variables
source $src_dir/.env

main() {
    mode="$1"
    echo "Manage valmi-activation services:"
    echo "Mode: ${mode}"

    cd $src_dir
    echo "Working directory: $PWD"

    echo "${@:2}"
    
    docker compose -f docker-compose.yml -f docker-compose.$mode.yml ${@:2}
}

main "$@"
