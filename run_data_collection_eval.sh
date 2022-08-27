#!/bin/bash

if [ $# != 2 ]; then
    echo "Usage: ./run_data_collection_eval.sh <storage_path> <dataset_name>"
    exit 1
fi

declare -A datasets=( ["defects4j"]="data/defects4j" 
                        ["bears"]="data/bears-benchmark" 
                        ["bugsdotjar"]="data/bugs-dot-jar" 
                        ["quixbugs"]="data/QuixBugs")

if [[ ! " ${!datasets[*]} " =~ " $2 " ]]; then
    echo "Dataset not found. Please use one of the following: ${!datasets[@]}"
    exit 1
fi

python src/checkout.py --storage $1 --$2 ${datasets[$2]} > $1/$2_checkout.out 2>&1
python src/filter_single_hunk.py --storage $1 --$2 ${datasets[$2]} --model_output $2_hunk.json > $1/$2_hunk.out 2>&1
python src/generate_test_samples.py --storage $1 --$2 ${datasets[$2]} --model_input $2_hunk.json --perturbation_model perturbation-0.0.1-SNAPSHOT-jar-with-dependencies.jar --test --model_output $2_test_samples.json > $1/$2_generate_test_samples.out 2>&1
