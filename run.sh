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
    ./run.sh stop prod/dev
    ./run.sh start prod/dev
    ./run.sh restart prod/dev
    
    Script to manage valmi-activaiton services.
    '
    exit
fi

src_dir="$(cd "$(dirname "$0")"; pwd -P)"

#Apply all environment variables
source $src_dir/.env

main() {
    action="$1"
    echo "Manage valmi-activation services:"
    echo "Action: ${action}"

    cd $src_dir
    echo "Working directory: $PWD"

    echo $DAGSTER_POSTGRES_USER

    option_two="$2"
    if [ -z "$option_two" ]; then
        echo "stage ("prod" or "dev") is not given, exiting.."
        exit
    fi

    if [[ $action == "stop" ]]; then
        docker compose -f docker-compose.yml -f docker-compose.$option_two.yml \
            --profile $option_two stop
        docker container prune -f
    elif [[ $action == "start" ]]; then
        docker compose -f docker-compose.yml -f docker-compose.$option_two.yml \
            --profile $option_two up -d --quiet-pull
    elif [[ $action == "restart" ]]; then
        docker compose -f docker-compose.yml -f docker-compose.$option_two.yml \
            --profile $option_two stop
        docker container prune -f
        docker compose -f docker-compose.yml -f docker-compose.$option_two.yml \
            --profile $option_two up -d --quiet-pull
    else
        echo Given action is not supported
        exit
    fi
}

main "$@"
