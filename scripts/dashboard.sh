#!/bin/bash

cd /home/vagrant/capstone2021
source .venv/bin/activate
sudo python3 src/c21server/dashboard/dashboard_server.py
