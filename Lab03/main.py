import json
import pandas as pd
from lab03 import Network

f = open('nodes.json')
nodes_dict = json.load(f)
f.close()
# print(nodes_dict)
cols = ['Path', 'Tot_lat [s]', 'Tot_noise [W]', 'SNR [dB]']
network_df = pd.DataFrame()

paths = []
network = Network(nodes_dict)
for node1 in network.nodes.keys():
    for node2 in network.nodes.keys():
        if node1 != node2:
            paths += network.find_paths(node1, node2)

network_df['Path'] = paths
# for path in paths:
