#!/bin/bash

if [ $# != 3 ]; then
    echo "Usage: ./run_train.sh <storage_path> <model_storage> <direction>"
    exit 1
fi

python src/train_model.py --storage $1 --model_input defects4j.json --defects4j "data/defects4j" --model_storage $2 --$3 --max_epochs 2 --samples_per_epoch 30000000 > $2/training_logs.out 2>&1
