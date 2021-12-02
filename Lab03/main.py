import json
import pandas as pd
from lab03 import Network

f = open('nodes.json')
nodes_dict = json.load(f)
f.close()
# print(nodes_dict)

nodes_frame = pd.DataFrame.from_dict(nodes_dict)
# print('\n', nodes_frame)
nnodes = Network(nodes_dict)
# Network.draw(nnodes)
path = nnodes.find_paths('A', 'B')
print(path)

connections = nnodes.connect()


