default: help

all : help install_venv clean_venv test start_main start_dev_mode_main
.PHONY : all

help:  # show help for each of the makefile recipes
	@grep -E '^[a-zA-Z0-9 -_]+:.*#'  Makefile | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

install_venv:  # install python virtual environment and requirements in it
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt

clean_venv:  # clean python virtual environment and requirements in it
	rm -rf venv

test:  # test cyberdBot
	. venv/bin/activate; python3 -m pytest -s -v *.py src/*.py

start_main:  # start main bot
	. venv/bin/activate; python3 main.py

start_dev_mode_main: export VALIDATOR_QUERY=cat\ .\/tests\/validators_query_test
start_dev_mode_main:  # start main bot in development mode for easy bot stop
	. venv/bin/activate; python3 main.py --dev_mode

start_scheduler:  # start scheduler
	. venv/bin/activate; python3 monitoring_scheduler.py

start_dev_mode_scheduler: export VALIDATOR_QUERY=cat\ .\/tests\/validators_query_test
start_dev_mode_scheduler:  # start scheduler in development mode for easy bot stop
	. venv/bin/activate; python3 monitoring_scheduler.py --dev_mode
