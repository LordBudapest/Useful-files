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

    graph = {
        "nodes": [],
        "outEdges": [],
        "inEdges": [],
        "edgeAttr": []
    }

    section = None

    for line in rawGraph:

        line = line.strip()

        if not line:
            continue

        # section switches
        if line == "Nodes":
            section = "nodes"
            continue

        elif line == "outEdge":
            section = "outEdges"
            continue

        elif line == "inEdge":
            section = "inEdges"
            continue

        elif line == "edgeAttr":
            section = "edgeAttr"
            continue

        # collect data
        try:
            if section == "nodes":
                graph["nodes"].append(line)

            elif section == "outEdges":
                graph["outEdges"].append(int(line))

            elif section == "inEdges":
                graph["inEdges"].append(int(line))

            elif section == "edgeAttr":
                graph["edgeAttr"].append(int(line))

        except Exception:
            continue

    safe_name = (
        os.path.relpath(filename, DATASET_DIR)
        .replace("/", "__")
    )

    out_file = (
        "../../data/graphs/" + safe_name + ".json"
    )

    with open(out_file, "w") as f:
        json.dump(graph, f)


# --------------------------------
# Graph Builder
# --------------------------------
def handler(filename):

    proc = Popen(
		[
	    "graph-builder",
	    "--print",
	    "--ast",
	    "--icfg",
	    "--data",
	    "--call",
	    filename
		],
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
    if stderr:
        print(stderr.decode("utf-8"))
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
