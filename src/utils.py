import argparse
import json
import subprocess
import pathlib

from serialization.encoders import BugEncoder, DatasetEncoder
from serialization.decoders import DatasetDecoder


def get_diff(source: pathlib.Path, target: pathlib.Path) -> str:
    cmd = "find {} {} -type f ! -name '*.java' -printf '%f\n' | diff -N -u -r {} {} -X -".format(source, target, source, target)
    run = subprocess.run(cmd, shell=True, capture_output=True)
    return run.stdout.decode("utf-8")


def get_default_json_filename(args):
    if args.defects4j != None:
        return "defects4j.json"
    elif args.bugsdotjar != None:
        return "bugsdotjar.json"
    elif args.bears != None:
        return "bears.json"
    elif args.quixbugs != None:
        return "quixbugs.json"


def get_json_input_file(args):
    if args.model_input != None:
        return pathlib.Path(args.storage, args.model_input).absolute()
    else:
        return pathlib.Path(args.storage, get_default_json_filename(args)).absolute()


def get_json_output_file(args):
    if args.model_output != None:
        return pathlib.Path(args.storage, args.model_output).absolute()
    else:
        return pathlib.Path(args.storage, get_default_json_filename(args)).absolute()


def save_dataset(args, dataset):
    with open(get_json_output_file(args), "w+") as f:
        json.dump(dataset, f, cls=DatasetEncoder, indent=4)


def load_dataset(args):
    if get_json_input_file(args).exists():
        with open(get_json_input_file(args), "r") as f:
            return json.load(f, cls=DatasetDecoder)
    else:
        raise Exception("Input file does not exist")


def add_core_args(parser):
    # Storage args
    parser.add_argument("--storage", help="Path to the storage directory", required=True, metavar="<path_to_storage>")
    parser.add_argument("--model_input", help="Path to the input json dump of the model. Defaults to <path_to_storage>/<dataset>.json", required=False, metavar="<path_to_input_json_file>")
    parser.add_argument("--model_output", help="Path to the output json dump of the model. Defaults to <path_to_storage>/<dataset>.json", required=False, metavar="<path_to_output_json_file>")

    # Dataset to analyze args
    dataset_arg = parser.add_mutually_exclusive_group(required=True)
    dataset_arg.add_argument("--defects4j", help="Path to the Defects4J directory", required=False, metavar="<path_to_defects4j>")
    dataset_arg.add_argument("--bugsdotjar", help="Path to the Bugs.jar directory", required=False, metavar="<path_to_bears>")
    dataset_arg.add_argument("--bears", help="Path to the Bears directory", required=False, metavar="<path_to_bears>")
    dataset_arg.add_argument("--quixbugs", help="Path to the QuixBugs directory", required=False, metavar="<path_to_quixbugs>")


    return parser
