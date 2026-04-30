#!/bin/bash
# Zoho Gym Campaigns - Automated Runner
# This script loads config and runs the skill
# Can be scheduled with cron or Task Scheduler

cd "$(dirname "$0")"
source config.txt
python3 main.py
