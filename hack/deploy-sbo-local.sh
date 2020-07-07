#!/bin/bash

SBO_LOCAL_LOG=out/sbo-local.log

make local > $SBO_LOCAL_LOG 2>&1 &

SBO_PID=$!

attempts=12
while [ -z "$(grep 'Starting workers' $SBO_LOCAL_LOG)" ]; do
    if [[ $attempts -ge 0 ]]; then
        sleep 5
        attempts=$((attempts-1))
    else
        echo "FAILED"
        kill $SBO_PID
        exit 1
    fi
done

echo $SBO_PID