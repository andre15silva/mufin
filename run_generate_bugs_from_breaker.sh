#!/bin/bash

if [ $# != 5 ]; then
    echo "Usage: ./run_generate_bugs_from_breaker.sh <storage_path> <dataset_name> <experiments_path> <experiment_name> <round>"
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

python src/generate_bugs_from_breaker.py --storage $1 --$2 ${datasets[$2]} --from_pretrained $3/$4/$5/fixer --beam_width 1 --model_input $2_hunk_compile_test.json --model_output $2_breaker_generated_bugs_$4_$5.json > $1/$2_breaker_generated_bugs_$4_$5.out 2>&1

if [[ "$5" == *"nocritic"* ]]; then
    python src/filter_single_hunk.py --storage $1 --$2 ${datasets[$2]} --model_input $2_breaker_generated_bugs_$4_$5.json --model_output $2_breaker_generated_bugs_$4_$5_hunk.json > $1/$2_breaker_generated_bugs_$4_$5_hunk.out 2>&1
fi

if [[ "$5" == *"compiler"* ]]; then
    python src/filter_single_hunk.py --storage $1 --$2 ${datasets[$2]} --model_input $2_breaker_generated_bugs_$4_$5.json --model_output $2_breaker_generated_bugs_$4_$5_hunk.json > $1/$2_breaker_generated_bugs_$4_$5_hunk.out 2>&1
    python src/filter_compile.py --storage $1 --$2 ${datasets[$2]} --model_input $2_breaker_generated_bugs_$4_$5_hunk.json --model_output $2_breaker_generated_bugs_$4_$5_hunk_compile.json > $1/$2_breaker_generated_bugs_$4_$5_hunk_compile.out 2>&1
fi

if [[ "$5" == *"tests"* ]]; then
    python src/filter_single_hunk.py --storage $1 --$2 ${datasets[$2]} --model_input $2_breaker_generated_bugs_$4_$5.json --model_output $2_breaker_generated_bugs_$4_$5_hunk.json > $1/$2_breaker_generated_bugs_$4_$5_hunk.out 2>&1
    python src/filter_compile.py --storage $1 --$2 ${datasets[$2]} --model_input $2_breaker_generated_bugs_$4_$5_hunk.json --model_output $2_breaker_generated_bugs_$4_$5_hunk_compile.json > $1/$2_breaker_generated_bugs_$4_$5_hunk_compile.out 2>&1
    python src/filter_test.py --storage $1 --$2 ${datasets[$2]} --model_input $2_breaker_generated_bugs_$4_$5_hunk_compile.json --model_output $2_breaker_generated_bugs_$4_$5_hunk_compile_test.json > $1/$2_breaker_generated_bugs_$4_$5_hunk_compile_test.out 2>&1
fi
