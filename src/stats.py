import argparse
import sys
import pandas as pd
import pathlib

import utils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to remove all bugs with non-single file patches.")
    parser = utils.add_core_args(parser)
    args = parser.parse_args()

    # Load the dataset
    dataset = utils.load_dataset(args)

    # Compute stats
    key = utils.get_json_input_file(args).stem
    data = {key : {}}
    data[key]["n_bugs"] = len(dataset.get_bugs())

    # Save stats to csv file
    df = pd.DataFrame.from_dict(data, orient="index")
    df.to_csv(pathlib.Path(args.storage, key + ".csv"))
