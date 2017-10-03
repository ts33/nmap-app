#!/usr/bin/env bash

# clear up stacks and exit swarm
docker stack rm nmap-app
docker swarm leave --force

# create postgres empty data directory
mkdir -p data/postgres/data

# rebuild owl
docker build -t nmap-app-owl ./owl

# rebuild ostrich
docker build -t nmap-app-ostrich ./ostrich

# setup swarm and deploy stack
docker swarm init
. ./env_docker && docker stack deploy -c stack.yml nmap-app
