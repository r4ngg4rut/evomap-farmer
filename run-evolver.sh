#!/bin/bash
cd /root/evomap-farmer
export A2A_HUB_URL=https://evomap.ai
export EVOLVER_NODE_SECRET=$(cat /root/.evomap/node_secret)
export EVOLVER_VALIDATOR_ENABLED=1

# Run single evolution cycle
evolver run --loop >> /root/evomap-farmer/logs/evolver-cron.log 2>&1
echo "[$(date)] Evolution cycle completed" >> /root/evomap-farmer/logs/evolver-cron.log
