import json

from models.bug import Bug
from models.dataset import Dataset

class BugEncoder(json.JSONEncoder):
    
    def default(self, obj):
        if isinstance(obj, Bug):
            bug = obj.__dict__
            bug["path"] = str(bug["path"])
            return bug
        return json.JSONEncoder.default(self, obj)


class DatasetEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Dataset):
            dataset = obj.__dict__
            dataset["bugs"] = [BugEncoder.default(self, x) for x in dataset["bugs"]]
            dataset["path"] = str(dataset["path"])
            if "bin" in dataset:
                del dataset["bin"]
            return dataset
        return json.JSONEncoder.default(self, obj)
