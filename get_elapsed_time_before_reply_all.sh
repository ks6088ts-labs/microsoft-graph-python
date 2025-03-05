#!/bin/bash

# Channels:
channels=(
    # set the channel ids here
    channel1_thread.skype
    channel2_thread.skype
    channel3_thread.skype
)

mkdir -p logs

for channel in "${channels[@]}"
do
    echo "Processing channel: $channel"
    uv run python scripts/main.py get-elapsed-time-before-reply --channel-id $channel 2>&1 | tee logs/$channel.log &
done
wait
