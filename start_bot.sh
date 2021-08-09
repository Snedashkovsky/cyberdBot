#!/bin/bash

SERVICE=$1
MODE=$2

# Check for Development Mode
case "$MODE" in
    d|dev|development)
        export DEV_MODE=1
        export VALIDATOR_QUERY=cat\ .\/tests\/validators_query_test
        ;;
    "")
        export DEV_MODE=0
        ;;
    *)
        echo $"Usage: $0 {m|main|s|scheduler} {null|d|dev|development}"
        exit 1
        ;;
esac

# Chose of service main or scheduler
case "$SERVICE" in
		m|main)
        python3 main.py
		    ;;
		s|scheduler)
        python3 monitoring_scheduler.py
		    ;;
    *)
        echo $"Usage: $0 {m|main|s|scheduler} {null|d|dev|development}"
        exit 1
        ;;
esac