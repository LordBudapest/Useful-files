import json
import sys
import networkx as nx
from pyvis.network import Network

# --------------------------------
# Read JSON path
# --------------------------------

if len(sys.argv) < 2:
    print("Usage: python visualize.py graph.json")
    sys.exit(1)

json_path = sys.argv[1]

# --------------------------------
# Load JSON
# --------------------------------

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

nodes = data["nodes"]
outEdges = data.get("outEdges", {})
inEdges = data.get("inEdges", {})
edgeAttr = data.get("edgeAttr", {})

# --------------------------------
# Edge type -> color mapping
# --------------------------------

EDGE_COLORS = {
    0: "blue",      # AST
    1: "red",       # CFG
    2: "green",     # Data Flow
    3: "orange",    # Call Graph
    4: "purple"
}

DEFAULT_COLOR = "gray"

# --------------------------------
# Build graph
# --------------------------------

G = nx.DiGraph()

# Add nodes
for node_id, label in nodes.items():
    G.add_node(int(node_id), label=label)

visited_edges = set()

# Add outEdges
for src, dst in outEdges.items():

    src = int(src)
    dst = int(dst)

    edge = (src, dst)

    if edge in visited_edges:
        continue

    visited_edges.add(edge)

    attr = edgeAttr.get(str(src), -1)

    color = EDGE_COLORS.get(attr, DEFAULT_COLOR)

    G.add_edge(
        src,
        dst,
        color=color,
        title=f"type={attr}"
    )

# Add inEdges (optional)
for dst, src in inEdges.items():

    src = int(src)
    dst = int(dst)

    edge = (src, dst)

    if edge in visited_edges:
        continue

    visited_edges.add(edge)

    attr = edgeAttr.get(str(src), -1)

    color = EDGE_COLORS.get(attr, DEFAULT_COLOR)

    G.add_edge(
        src,
        dst,
        color=color,
        title=f"type={attr}"
    )

# --------------------------------
# Visualize
# --------------------------------

net = Network(
    height="800px",
    width="100%",
    directed=True,
    notebook=False
)

net.from_nx(G)

# Node styling
for node in net.nodes:
    node_id = str(node["id"])

    if node_id in nodes:
        node["label"] = nodes[node_id]

    node["size"] = 20

# Better physics
net.barnes_hut()

# Add legend manually
legend_html = """
<div style="
position: fixed;
top: 10px;
right: 10px;
background: white;
padding: 10px;
border: 1px solid black;
z-index:9999;
font-family:Arial;
">
<b>Edge Types</b><br>
<span style="color:blue;">■</span> AST<br>
<span style="color:red;">■</span> CFG<br>
<span style="color:green;">■</span> Data Flow<br>
<span style="color:orange;">■</span> Call Graph<br>
</div>
"""

net.html += legend_html

net.write_html("graph.html")

print("Saved to graph.html")