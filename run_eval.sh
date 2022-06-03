#!/bin/bash

if [ $# != 6 ]; then
    echo "Usage: ./run_eval.sh <storage_path> <dataset_name> <model_path> <beam_width> <beam_groups> <repetition_penalty>"
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

python src/eval_model.py --storage $1 --$2 ${datasets[$2]} --model_input $2_hunk_compile_test.json --model_output $2_hunk_compile_test.json --from_pretrained $3 --beam_width $4 --beam_groups $5 --repetition_penalty $6 --results_file $3/eval_$2_bw_$4_bg_$5_rp_$6.json > $3/eval_$2_bw_$4_bg_$5_rp_$6.out 2>&1
