import pathlib
import subprocess

from bug import Bug
from dataset import Dataset
from defects4j.defects4jbug import Defects4JBug

class Defects4J(Dataset):

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__("defects4j", path)
        self.bin = path.joinpath("framework/bin/defects4j")

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
                fixed_path = pathlib.Path(storage, self.identifier, "%s-%d-fixed" % (pid, bid)).absolute()
                if buggy_path.exists() or fixed_path.exists(): continue
                buggy_path.mkdir(parents=True)
                fixed_path.mkdir(parents=True)

                try:
                    run = subprocess.run("%s checkout -p %s -v %db -w %s" % (self.bin, pid, bid, buggy_path), shell=True, capture_output=True, check=True)
                    run = subprocess.run("%s checkout -p %s -v %df -w %s" % (self.bin, pid, bid, fixed_path), shell=True, capture_output=True, check=True)
                    self.add_bug(Defects4JBug("%s-%d" % (pid, bid), buggy_path, True))
                    self.add_bug(Defects4JBug("%s-%d" % (pid, bid), fixed_path, False))
                except subprocess.CalledProcessError:
                    finished = False
                    buggy_path.rmdir()
                    fixed_path.rmdir()
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
                buggy_path = pathlib.Path(storage, self.identifier, "%s-%d-buggy" % (pid, bid), "defects4j.build.properties").absolute()
                fixed_path = pathlib.Path(storage, self.identifier, "%s-%d-fixed" % (pid, bid), "defects4j.build.properties").absolute()
                if not buggy_path.exists() or not fixed_path.exists():
                    missing.add(pid + "-" + bid)

        return len(missing) == 0
