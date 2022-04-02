import pathlib
import subprocess
import shutil

import utils
from models.bug import Bug
from models.dataset import Dataset
from models.defects4j.defects4jbug import Defects4JBug

class Defects4J(Dataset):

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__("defects4j", path)
        self.bin = path.joinpath("framework/bin/defects4j")


    def checkout_oldests(self, storage: pathlib.Path) -> None:
        # Get all project ids
        run = subprocess.run("%s pids" % self.bin, shell=True, capture_output=True, check=True)
        pids = {pid.decode("utf-8") for pid in run.stdout.split()}

        # Get all bug ids for all pids
        bugs = {}
        for pid in pids:
            run = subprocess.run("%s bids -p %s" % (self.bin, pid), shell=True, capture_output=True, check=True)
            bugs[pid] = {int(bid.decode("utf-8")) for bid in run.stdout.split()}
            print("Found %3d bugs for project %s" % (len(bugs[pid]), pid))

        # TODO: choose the oldest for each pid

        # Checkout fixed version
        for pid in pids:
            for bid in bugs[pid]:
                print("Checking out %s-%d" % (pid, bid))
                fixed_path = pathlib.Path(storage, self.identifier, "%s-%d" % (pid, bid)).absolute()
                if fixed_path.exists(): continue
                fixed_path.mkdir(parents=True)

                try:
                    # Get fixed version
                    run = subprocess.run("%s checkout -p %s -v %df -w %s" % (self.bin, pid, bid, fixed_path), shell=True, capture_output=True, check=True)
                    # Store bug pointing to the fixed version
                    self.add_bug(Defects4JBug("%s-%d" % (pid, bid), fixed_path, ""))
                except subprocess.CalledProcessError as e:
                    finished = False
                    shutil.rmtree(fixed_path)
                    continue


    def check_oldests(self, storage: pathlib.Path) -> bool:
        # Get all project ids
        run = subprocess.run("%s pids" % self.bin, shell=True, capture_output=True, check=True)
        pids = {pid.decode("utf-8") for pid in run.stdout.split()}

        # Get all bug ids for all pids
        bugs = {}
        for pid in pids:
            run = subprocess.run("%s bids -p %s" % (self.bin, pid), shell=True, capture_output=True, check=True)
            bugs[pid] = {int(bid.decode("utf-8")) for bid in run.stdout.split()}
            print("Found %3d bugs for project %s" % (len(bugs[pid]), pid))

        # TODO: choose the oldest for each pid

        missing = set()
        # Check fixed versions
        for pid in pids:
            for bid in bugs[pid]:
                fixed_path = pathlib.Path(storage, self.identifier, "%s-%d" % (pid, bid), "defects4j.build.properties").absolute()
                if not fixed_path.exists():
                    print("Missing %s-%d" % (pid, bid))
                    missing.add("%s-%d" % (pid, bid))

        return len(missing) == 0


    def checkout_all(self, storage: pathlib.Path) -> None:
        # Get all project ids
        run = subprocess.run("%s pids" % self.bin, shell=True, capture_output=True, check=True)
        pids = {pid.decode("utf-8") for pid in run.stdout.split()}

        # Get all bug ids for all pids
        bugs = {}
        for pid in pids:
            run = subprocess.run("%s bids -p %s" % (self.bin, pid), shell=True, capture_output=True, check=True)
            bugs[pid] = {int(bid.decode("utf-8")) for bid in run.stdout.split()}
            print("Found %3d bugs for project %s" % (len(bugs[pid]), pid))

        # Checkout all buggy and fixed versions
        for pid in pids:
            for bid in bugs[pid]:
                print("Checking out %s-%d" % (pid, bid))
                buggy_path = pathlib.Path(storage, self.identifier, "%s-%d-buggy" % (pid, bid)).absolute()
                fixed_path = pathlib.Path(storage, self.identifier, "%s-%d" % (pid, bid)).absolute()
                if buggy_path.exists() or fixed_path.exists(): continue
                buggy_path.mkdir(parents=True)
                fixed_path.mkdir(parents=True)

                try:
                    # Get both versions
                    run = subprocess.run("%s checkout -p %s -v %db -w %s" % (self.bin, pid, bid, buggy_path), shell=True, capture_output=True, check=True)
                    run = subprocess.run("%s checkout -p %s -v %df -w %s" % (self.bin, pid, bid, fixed_path), shell=True, capture_output=True, check=True)
                    # Store bug patch pointing to the fixed version
                    self.add_bug(Defects4JBug("%s-%d" % (pid, bid), fixed_path, utils.get_diff(fixed_path, buggy_path)))
                    # Remove buggy codebase
                    shutil.rmtree(buggy_path)
                except subprocess.CalledProcessError:
                    finished = False
                    shutil.rmtree(buggy_path)
                    shutil.rmtree(fixed_path)
                    continue


    def check_integrity(self, storage: pathlib.Path) -> bool:
        # Get all project ids
        run = subprocess.run("%s pids" % self.bin, shell=True, capture_output=True, check=True)
        pids = {pid.decode("utf-8") for pid in run.stdout.split()}

        # Get all bug ids for all pids
        bugs = {}
        for pid in pids:
            run = subprocess.run("%s bids -p %s" % (self.bin, pid), shell=True, capture_output=True, check=True)
            bugs[pid] = {int(bid.decode("utf-8")) for bid in run.stdout.split()}
            print("Found %3d bugs for project %s" % (len(bugs[pid]), pid))

        missing = set()
        # Checkout all buggy and fixed versions
        for pid in pids:
            for bid in bugs[pid]:
                fixed_path = pathlib.Path(storage, self.identifier, "%s-%d" % (pid, bid), "defects4j.build.properties").absolute()
                if not fixed_path.exists():
                    print("Missing %s-%d" % (pid, bid))
                    missing.add("%s-%d" % (pid, bid))

        return len(missing) == 0
