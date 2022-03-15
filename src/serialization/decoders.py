import json

from pathlib import Path

from defects4j.defects4j import Defects4J
from defects4j.defects4jbug import Defects4JBug
from bugsdotjar.bugsdotjar import BugsDotJar
from defects4j.defects4jbug import Defects4JBug
from bears.bears import Bears
from bears.bearsbug import BearsBug
from quixbugs.quixbugs import QuixBugs
from quixbugs.quixbugsbug import QuixBugsBug


class BugDecoder:

    @staticmethod
    def decode(data, dataset):
        bug = None

        if dataset == "bears":
            return BearsBug(data["identifier"], Path(data["path"]), data["buggy"])
        elif dataset == "bugsdotjar":
            return BugsDotJarBug(data["identifier"], Path(data["path"]), data["buggy"])
        elif dataset == "defects4j":
            return Defects4JBug(data["identifier"], Path(data["path"]), data["buggy"])
        elif dataset == "quixbugs":
            return QuixBugsBug(data["identifier"], Path(data["path"]), data["buggy"])
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
