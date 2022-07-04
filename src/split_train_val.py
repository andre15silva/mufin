import numpy as np
import argparse
import pathlib

from datasets import load_dataset

import utils
import serialization_utils
import model_utils


def split_train_val(args):
    # Load the dataset
    dataset = load_dataset("json", data_files=str(pathlib.Path(args.dataset).absolute()) + "/*.json", field="bugs")

    # Shuffle the dataset
    dataset["train"] = dataset["train"].shuffle(seed=42)

    # Split dataset into training and validation
    split_datasets = dataset["train"].train_test_split(train_size=0.98, seed=42)
    split_datasets["validation"] = split_datasets.pop("test")

    print(split_datasets)

    # Save the datasets
    split_datasets["train"].to_json(str(pathlib.Path(args.training_dataset).absolute()))
    split_datasets["validation"].to_json(str(pathlib.Path(args.validation_dataset).absolute()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script to shuffle and split a dataset into training and validation.")
    parser = utils.add_split_train_val_args(parser)
    args = parser.parse_args()

    split_train_val(args)
