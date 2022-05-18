import json
import pathlib

from serialization.encoders import BugEncoder, DatasetEncoder
from serialization.decoders import DatasetDecoder

from models.defects4j.defects4j import Defects4J
from models.bugsdotjar.bugsdotjar import BugsDotJar
from models.bears.bears import Bears
from models.quixbugs.quixbugs import QuixBugs


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


def save_dataset_to_file(args, dataset, file):
    with open(file, "w+") as f:
        json.dump(dataset, f, cls=DatasetEncoder, indent=4)


def save_dataset(args, dataset):
    save_dataset_to_file(args, dataset, get_json_output_file(args))


def load_dataset(args):
    if get_json_input_file(args).exists():
        with open(get_json_input_file(args), "r") as f:
            return json.load(f, cls=DatasetDecoder)
    else:
        raise Exception("Input file does not exist")


def create_empty_dataset(args):
    if args.defects4j != None:
        defects4j = Defects4J(pathlib.Path(args.defects4j).absolute())
        return defects4j
    elif args.bugsdotjar != None:
        bugsdotjar = BugsDotJar(pathlib.Path(args.bugsdotjar).absolute())
        return bugsdotjar
    elif args.bears != None:
        bears = Bears(pathlib.Path(args.bears).absolute())
        return bears
    elif args.quixbugs != None:
        quixbugs = QuixBugs(pathlib.Path(args.quixbugs).absolute())
        return quixbugs
    else:
        return NotImplementedError("%s" % args)
