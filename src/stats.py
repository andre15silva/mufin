import argparse
import sys
import pandas as pd
import pathlib
import subprocess
import json
from datetime import datetime

import utils
import serialization_utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to remove all bugs with non-single file patches.")
    parser = utils.add_core_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = serialization_utils.load_dataset(args)

    # Compute stats
    data = []
    for bug in dataset.get_bugs():
        bug_info = { 
                "identifier" : bug.get_identifier(),
                "project" : "",
                "commitid" : "",
                "date" : "",
                "loc" : "",
                "tests" : ""
                }

        # Read bears.json
        with open("/home/andre/Repos/mscthesis/storage/bears/Bears-1/bears.json", "r") as f:
            info = json.load(f)
            bug_info["project"] = info["repository"]["name"]
            bug_info["commitid"] = info["commits"]["fixerBuild"]["sha"][:6]

            date = datetime.strptime(info["commits"]["fixerBuild"]["date"], "%b %d, %Y %I:%M:%S %p")
            bug_info["date"] = date.strftime("%Y-%m-%d")

            cmd = "cd %s; find . -name '*.java' -and -not -path '*test*' -and -not -path '*Test*' | xargs cat | sed '/^\s*$/d' | wc -l"
            run = subprocess.run(cmd, shell=True, capture_output=True)
            bug_info["loc"] = int(run.stdout.decode("utf-8"))
            bug_info["tests"] = info["tests"]["overallMetrics"]["numberRunning"]

        data.append(bug_info)

    # Save stats to csv file
    df = pd.DataFrame(data)
    df = df.set_index("identifier")
    df = df.sort_index()
    key = serialization_utils.get_json_input_file(args).stem
    df.to_csv(pathlib.Path(args.storage, key + ".csv"))
