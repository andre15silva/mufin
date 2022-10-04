import argparse
import sys
import pandas as pd
import pathlib
import subprocess
import json
import tempfile
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

        # TODO: move this to model classes
        if "Bears" in bug.get_identifier():
            # Read bears.json
            with open(pathlib.Path(bug.get_path(), "bears.json"), "r") as f:
                info = json.load(f)
                bug_info["project"] = info["repository"]["name"]
                bug_info["commitid"] = info["commits"]["fixerBuild"]["sha"][:6]

                date = datetime.strptime(info["commits"]["fixerBuild"]["date"], "%b %d, %Y %I:%M:%S %p")
                bug_info["date"] = date.strftime("%Y-%m-%d")
        else:
            pid, bid = bug.get_identifier().split("-")
            bug_info["project"] = pid
            cmd = "%s info -p %s -b %s" % (dataset.get_path().joinpath("framework/bin/defects4j"), pid, bid)
            run = subprocess.run(cmd, shell=True, capture_output=True)
            lines = run.stdout.decode("utf-8").splitlines()
            for i, line in enumerate(lines):
                if "Revision ID (fixed version):" in line:
                    bug_info["commitid"] = lines[i+1].strip()[:6]
                if "Revision date (fixed version):" in line:
                    date = datetime.strptime(lines[i+1].strip(), "%Y-%m-%d %H:%M:%S %z")
                    bug_info["date"] = date.strftime("%Y-%m-%d")


        sources_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False)
        sources = pathlib.Path(bug.get_path()).glob("**/*.java")
        sources = [str(source.relative_to(pathlib.Path(bug.get_path()))) for source in sources]
        sources = filter(lambda source: "test" not in source and "Test" not in source, sources)
        sources_file.write("\n".join(str(source) for source in sources))
        sources_file.flush()
        sources_file.close()

        cmd = "cd %s; lizard -f %s -l java | tail -n 1" % (bug.get_path(), str(sources_file.name))
        run = subprocess.run(cmd, shell=True, capture_output=True)
        bug_info["loc"] = int(run.stdout.decode("utf-8").split()[0])

        tests_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=False)
        tests = pathlib.Path(bug.get_path()).glob("**/*.java")
        tests = [str(test.relative_to(pathlib.Path(bug.get_path()))) for test in tests]
        tests = filter(lambda test: "test" in test or "Test" in test, tests)
        tests_file.write("\n".join(str(test) for test in tests))
        tests_file.flush()
        tests_file.close()

        cmd = "cd %s; lizard -f %s -l java | tail -n 1" % (bug.get_path(), str(tests_file.name))
        run = subprocess.run(cmd, shell=True, capture_output=True)
        bug_info["tests"] = int(run.stdout.decode("utf-8").split()[4])

        data.append(bug_info)

    # Save stats to csv file
    df = pd.DataFrame(data)
    df = df.set_index("identifier")
    df = df.sort_index()
    key = serialization_utils.get_json_input_file(args).stem
    df.to_csv(pathlib.Path(args.storage, key + ".csv"))
