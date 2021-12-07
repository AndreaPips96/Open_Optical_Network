import json
import pandas as pd
import numpy as np
from useful_classes import Network
from useful_classes import SignalInformation

# Open and import JSON file
f = open('nodes.json')
nodes_dict = json.load(f)
f.close()
# print(nodes_dict)

# Initialize network DataFrame
network_df = pd.DataFrame()

# Build network
network = Network(nodes_dict)
# network.draw()
network.connect()

# Find all possible paths in the network
paths = []
for node1 in network.nodes.keys():
    for node2 in network.nodes.keys():
        if node1 != node2:
            paths += network.find_paths(node1, node2)
# Insert paths in network DataFrame
network_df['Path'] = paths

# Evaluate latency, noise power and SNR for each path
latencies = []
noise = []
snr = []
for path in paths:
    signal = SignalInformation(path)
    network.propagate(signal)
    latencies.append(signal.latency)
    noise.append(signal.noise_power)
    snr.append(10*np.log10(signal.signal_power/signal.noise_power))
# Insert latency, noise power and SNR in network DataFrame
network_df['Latency'] = latencies
network_df['Noise_power'] = noise
network_df['SNR'] = snr
# print(network_df)
