#!/bin/bash

if [ $# != 2 ]; then
    echo "Usage: ./run_pre_train.sh <storage_path> <model_storage>"
    exit 1
fi

python src/train_model.py --storage $1 --model_input defects4j.json --defects4j "data/defects4j" --model_storage $2 > $2/training_logs.out 2>&1