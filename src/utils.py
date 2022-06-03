import argparse
import json
import subprocess
import pathlib

def get_diff(source: pathlib.Path, target: pathlib.Path) -> str:
    cmd = "find {} {} -type f ! -name '*.java' -printf '%f\n' | diff -N -U 5 -r {} {} -X -".format(source, target, source, target)
    run = subprocess.run(cmd, shell=True, capture_output=True)
    return run.stdout.decode("utf-8", errors="ignore")


def add_core_args(parser):
    # Storage args
    parser.add_argument("--storage", help="Path to the storage directory", required=True, metavar="<path_to_storage>")
    parser.add_argument("--model_input", help="Name of the input json dump of the model. Defaults to <path_to_storage>/<dataset>.json", required=False, metavar="<model_input.json>")
    parser.add_argument("--model_output", help="Name of the output json dump of the model. Defaults to <path_to_storage>/<dataset>.json", required=False, metavar="<model_output.json>")

    # Dataset to analyze args
    dataset_arg = parser.add_mutually_exclusive_group(required=True)
    dataset_arg.add_argument("--defects4j", help="Path to the Defects4J directory", required=False, metavar="<path_to_defects4j>")
    dataset_arg.add_argument("--bugsdotjar", help="Path to the Bugs.jar directory", required=False, metavar="<path_to_bears>")
    dataset_arg.add_argument("--bears", help="Path to the Bears directory", required=False, metavar="<path_to_bears>")
    dataset_arg.add_argument("--quixbugs", help="Path to the QuixBugs directory", required=False, metavar="<path_to_quixbugs>")

    return parser


def add_filtering_args(parser):
    # Options for filtering
    parser.add_argument("--ignore_empty_diff", help="Ignores empty diffs during diff-based filtering", required=False, action="store_true")
    parser.add_argument("--keep_single_line_only", help="Keeps only single line diffs during diff-based filtering", required=False, action="store_true")

    return parser


def add_generation_args(parser):
    # Options for bug generation
    parser.add_argument("--perturbation_model", help="Path to jar file of the perturbation model", required=True, metavar="<path_to_perturbation_model_jar>")

    generation_strategy = parser.add_mutually_exclusive_group(required=True)
    generation_strategy.add_argument("--selfapr", help="Use the SelfAPR perturbation strategy", required=False, action="store_true")
    generation_strategy.add_argument("--buglab", help="Use the BugLab perturbation strategy", required=False, action="store_true")

    return parser


def add_train_args(parser):
    # Options for model training
    parser.add_argument("--from_pretrained", help="Path to the pretrained model. If not used a new model will be trained from scratch.", required=False, metavar="<path_to_pretrained_model>")
    parser.add_argument("--model_storage", help="Path to the location where to store the model in.", required=True, metavar="<path_to_save_dir>")

    # TODO: arguments for relevant model hyper-parameters
    # TODO: argument for setting fixed-to-buggy, or vice-verse

    return parser


def add_eval_args(parser):
    # Options for model training
    parser.add_argument("--from_pretrained", help="Path to the pretrained model.", required=True, metavar="<path_to_pretrained_model>")
    parser.add_argument("--results_file", help="Path to the result file", required=True, metavar="<path_to_result_file>")
    
    parser.add_argument("--beam_width", type=int, help="Beam width", required=True, metavar="<beam_width>")
    parser.add_argument("--beam_groups", type=int, help="Beam groups", required=True, metavar="<beam_groups>")
    parser.add_argument("--repetition_penalty", type=float, help="Beam groups", required=True, metavar="<repetition_penalty>")
    
    # TODO: argument for setting fixed-to-buggy, or vice-verse

    return parser
