import json

from pathlib import Path

from models.defects4j.defects4j import Defects4J
from models.defects4j.defects4jbug import Defects4JBug
from models.bugsdotjar.bugsdotjar import BugsDotJar
from models.bugsdotjar.bugsdotjar import BugsDotJarBug
from models.defects4j.defects4jbug import Defects4JBug
from models.bears.bears import Bears
from models.bears.bearsbug import BearsBug
from models.quixbugs.quixbugs import QuixBugs
from models.quixbugs.quixbugsbug import QuixBugsBug


class BugDecoder:

    @staticmethod
    def decode(data, dataset):
        bug = None

        if dataset == "bears":
            return BearsBug(data["identifier"], Path(data["path"]), data["diff"])
        elif dataset == "bugsdotjar":
            return BugsDotJarBug(data["identifier"], Path(data["path"]), data["diff"])
        elif dataset == "defects4j":
            return Defects4JBug(data["identifier"], Path(data["path"]), data["diff"])
        elif dataset == "quixbugs":
            return QuixBugsBug(data["identifier"], Path(data["path"]), data["diff"])
        else:
            raise NotImplementedError


class DatasetDecoder(json.JSONDecoder):

    def decode(self, s):
        data = json.loads(s)

        dataset = None
        if data["identifier"] == "bears":
            dataset = Bears(Path(data["path"]).absolute())
        elif data["identifier"] == "bugsdotjar":
            dataset = BugsDotJar(Path(data["path"]).absolute())
        elif data["identifier"] == "defects4j":
            dataset = Defects4J(Path(data["path"]).absolute())
        elif data["identifier"] == "quixbugs":
            dataset = QuixBugs(Path(data["path"]).absolute())
        else:
            raise NotImplementedError

        for bug in data["bugs"]:
            dataset.add_bug(BugDecoder.decode(bug, data["identifier"]))

        return dataset
