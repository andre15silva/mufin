#!/bin/bash

if [ $# != 3 ]; then
    echo "Usage: ./run_generate_bugs_from_perturbation_model.sh <storage_path> <dataset_name> <perturbation_strategy>"
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

python src/generate_bugs_from_pertubation_model.py --storage $1 --$2 ${datasets[$2]} --perturbation_model perturbation-0.0.1-SNAPSHOT-jar-with-dependencies.jar --model_input $2_hunk_compile_test.json --model_output $2_generated_bugs_$3.json --$3 > $1/$2_generated_bugs_$3.out 2>&1

# Filter each generated dataset
for i in  $(find $1 -type f -name "$2_generated_bugs_$3_*.json" -printf "%f\n")
do
    mkdir -p $1/generated_$2_$3/
    python src/filter_single_hunk.py --keep_single_file_only --keep_single_hunk_only --storage $1 --$2 ${datasets[$2]} --model_input $i --model_output generated_$2_$3/$i\_hunk.json > $1/$i\_hunk.out 2>&1
done
