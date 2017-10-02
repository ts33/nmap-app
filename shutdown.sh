#!/usr/bin/env bash

# clear up stacks and exit swarm
docker stack rm nmap-app
docker swarm leave --force
