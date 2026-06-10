import glob, json, tqdm, os, random
import multiprocessing as mp
import numpy as np

'''
File - prepData.py

This file will take the graphs produced by dataFormatter.py and
produce the final representation of the graphs. It will produce
the representation of each node in the graph for the GGNN to
perform calculations on. It will also produce a set of edge files
which will contain the edges
'''

graphs = glob.glob("../../data/graphs/*.json")

results = {}

for graph in graphs:
    name = os.path.basename(graph)
    results[name] = []

tokenDict = json.load(open("../../data/tokenDict.json"))


def makeFinalRep(graph):

    graph_path = "../../data/graphs/" + graph

    if graph_path not in graphs:
        return

    graphDict = json.load(open(graph_path))

    nodeRepresentations = []

    # --------------------------------
    # Node one-hot features
    # --------------------------------
    for token in graphDict["nodes"]:

        aList = np.array([0] * len(tokenDict))

        if token in tokenDict:
            aList[tokenDict[token]] = 1

        nodeRepresentations.append(aList)

    nodeRepresentations = np.array(nodeRepresentations)

    # --------------------------------
    # Edge buckets
    # --------------------------------
    ASTDict = []
    ICFGDict = []
    DataDict = []
    CallDict = []

    outEdges = graphDict["outEdges"]
    inEdges = graphDict["inEdges"]
    edgeAttrs = graphDict["edgeAttr"]


    for outNode, inNode, attr in zip(
        outEdges,
        inEdges,
        edgeAttrs
    ):

        edge = [outNode, inNode]
        # Final edge mapping
        if attr == 0:
            ASTDict.append(edge)

        elif attr == 1:
            ICFGDict.append(edge)

        elif attr == 2:
            CallDict.append(edge)

        elif attr == 3:
            DataDict.append(edge)


    # --------------------------------
    # Save edge tensors
    # --------------------------------
    np.savez_compressed(
        "../../data/final_graphs/" + graph + "Edges.npz",
        AST=np.array(ASTDict, dtype="long"),
        ICFG=np.array(ICFGDict, dtype="long"),
        Data=np.array(DataDict, dtype="long"),
        Call=np.array(CallDict, dtype="long")
    )

    # --------------------------------
    # Save node features
    # --------------------------------
    np.savez_compressed(
        "../../data/final_graphs/" + graph + ".npz",
        node_rep=nodeRepresentations
    )
pool = mp.Pool(mp.cpu_count()-2)
result_object = [pool.apply_async(makeFinalRep, args=([key.split("|||")[0]])) for key in results]

thing = [r.get() for r in tqdm.tqdm(result_object)]

pool.close()
