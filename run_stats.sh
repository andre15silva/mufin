#!/bin/bash

python src/stats.py --storage remote/ --defects4j ./ --model_input defects4j.json
python src/stats.py --storage remote/ --defects4j ./ --model_input defects4j_diff.json
python src/stats.py --storage remote/ --defects4j ./ --model_input defects4j_diff_compile.json
python src/stats.py --storage remote/ --defects4j ./ --model_input defects4j_diff_compile_test.json

python src/stats.py --storage remote/ --bugsdotjar ./ --model_input bugsdotjar.json
python src/stats.py --storage remote/ --bugsdotjar ./ --model_input bugsdotjar_diff.json
python src/stats.py --storage remote/ --bugsdotjar ./ --model_input bugsdotjar_diff_compile.json
python src/stats.py --storage remote/ --bugsdotjar ./ --model_input bugsdotjar_diff_compile_test.json

python src/stats.py --storage remote/ --quixbugs ./ --model_input quixbugs.json
python src/stats.py --storage remote/ --quixbugs ./ --model_input quixbugs_diff.json
python src/stats.py --storage remote/ --quixbugs ./ --model_input quixbugs_diff_compile.json
python src/stats.py --storage remote/ --quixbugs ./ --model_input quixbugs_diff_compile_test.json

python src/stats.py --storage remote/ --bears ./ --model_input bears.json
python src/stats.py --storage remote/ --bears ./ --model_input bears_diff.json
python src/stats.py --storage remote/ --bears ./ --model_input bears_diff_compile.json
python src/stats.py --storage remote/ --bears ./ --model_input bears_diff_compile_test.json
