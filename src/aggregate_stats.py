import argparse
import sys
import pandas as pd
import pathlib

import utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to remove all bugs with non-single file patches.")
    parser.add_argument("--storage", help="Path to the storage directory", required=True, metavar="<path_to_storage>")
    args = parser.parse_args()


    # Aggregate all csv files except from final result
    csv_files = pathlib.Path(args.storage).glob("*.csv")
    dfs = [pd.read_csv(file, index_col=[0]) for file in csv_files if file.stem != "results"]
    result = pd.concat(dfs).sort_index()

    # Store result
    print(result.to_markdown())
    result.to_csv(pathlib.Path(args.storage, "results.csv"))
