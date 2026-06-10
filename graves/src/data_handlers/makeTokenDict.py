import glob
import json
import tqdm

files = glob.glob("../../data/graphs/*.json")

tokenSet = set()

for aFile in tqdm.tqdm(files):
    myDict = json.load(open(aFile))

    for token in myDict["nodes"]:
        tokenSet.add(token)

tokenDict = {}

for idx, item in enumerate(sorted(tokenSet)):
    tokenDict[item] = idx

json.dump(
    tokenDict,
    open("../../data/tokenDict.json", "w"),
    indent=2
)
