import os
import glob
import json
import random
import tqdm
from subprocess import Popen, PIPE
import multiprocessing as mp

# --------------------------------
# CONFIG
# --------------------------------
DATASET_DIR = "../../my_dataset"

VERIFIERS = [
    "VerifierA",
    "VerifierB",
    "VerifierC"
]

TRAIN_SPLIT = 0.80
VAL_SPLIT = 0.10
TEST_SPLIT = 0.10

random.seed(42)

# --------------------------------
# Make folders
# --------------------------------
os.makedirs("../../data/graphs", exist_ok=True)
os.makedirs("../../data/final_graphs", exist_ok=True)

# --------------------------------
# Find C files
# --------------------------------
files = glob.glob(
    os.path.join(DATASET_DIR, "**/*.c"),
    recursive=True
)

print(f"Found {len(files)} files")

random.shuffle(files)

n = len(files)
train_end = int(n * TRAIN_SPLIT)
val_end = train_end + int(n * VAL_SPLIT)

train_files = files[:train_end]
val_files = files[train_end:val_end]
test_files = files[val_end:]

print(
    f"Train={len(train_files)} "
    f"Val={len(val_files)} "
    f"Test={len(test_files)}"
)

# --------------------------------
# Graph Parsing
# --------------------------------
def parseGraph(filename, rawGraph):
    ptrToToken = {}

    graph = {
        "tokens": {},
        "AST": {},
        "ICFG": {},
        "Data": {}
    }

    for line in rawGraph:

        line = line.strip()

        if not line:
            continue

        line = line.replace("(void)", "")
        line = line.replace(")", "")
        line = line.replace("(", "")

        parts = line.split(",")

        try:
            kind = parts[0]

            if kind == "AST":

                if parts[1] not in ptrToToken:
                    ptrToToken[parts[1]] = parts[2]

                if parts[3] not in ptrToToken:
                    ptrToToken[parts[3]] = parts[4]

                graph["tokens"] = ptrToToken

                graph["AST"].setdefault(
                    parts[1], []
                ).append(parts[3])

            elif kind == "CFG":
                graph["ICFG"].setdefault(
                    parts[2], []
                ).append(parts[4])

            elif kind == "DFG":
                graph["Data"].setdefault(
                    parts[1], []
                ).append(parts[3])

        except Exception:
            continue

    safe_name = (
    	os.path.relpath(filename, DATASET_DIR).replace("/","__")
    )
    out_file = (
    	"../../data/graphs/"+safe_name+".json"
    )

    json.dump(graph, open(out_file, "w"))


# --------------------------------
# Graph Builder
# --------------------------------
def handler(filename):

    proc = Popen(
        ["graph-builder", filename],
        stdout=PIPE,
        stderr=PIPE
    )

    stdout, stderr = proc.communicate()

    if stdout:
        stdout = stdout.decode("utf-8")

        graph = [
            x for x in stdout.split("\n")
            if x.strip()
        ]

        parseGraph(filename, graph)

        return None

    print("FAILED:", filename)
    return filename


pool = mp.Pool(max(1, mp.cpu_count() - 2))

jobs = [
    pool.apply_async(handler, args=(f,))
    for f in files
]

[r.get() for r in tqdm.tqdm(jobs)]

pool.close()

# --------------------------------
# Random ranking generator
# --------------------------------
def make_random_ranking():

    ranking = [1, 2, 3]
    random.shuffle(ranking)

    return [
        [VERIFIERS[i], ranking[i]]
        for i in range(3)
    ]


def build_split(file_list):

    out = {}

    for f in file_list:
        key = (
        	os.path.relpath(f, DATASET_DIR).replace("/","__")+".json"
        )
        out[key] = make_random_ranking()

    return out


train_json = build_split(train_files)
val_json = build_split(val_files)
test_json = build_split(test_files)

json.dump(
    train_json,
    open("../../data/customTrainFiles.json", "w"),
    indent=2
)

json.dump(
    val_json,
    open("../../data/customValFiles.json", "w"),
    indent=2
)

json.dump(
    test_json,
    open("../../data/customTestFiles.json", "w"),
    indent=2
)

print("Done.")
