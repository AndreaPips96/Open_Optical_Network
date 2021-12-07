import json
import pandas as pd
import numpy as np
from lab03 import Network
from lab03 import SignalInformation


f = open('nodes.json')
nodes_dict = json.load(f)
f.close()
# print(nodes_dict)
network_df = pd.DataFrame()

paths = []
network = Network(nodes_dict)
network.connect()
for node1 in network.nodes.keys():
    for node2 in network.nodes.keys():
        if node1 != node2:
            paths += network.find_paths(node1, node2)
network_df['Path'] = paths

latencies = []
noise = []
snr = []
for path in paths:
    signal = SignalInformation(path)
    network.propagate(signal)
    latencies.append(signal.latency)
    noise.append(signal.noise_power)
    snr.append(10*np.log10(signal.signal_power/signal.noise_power))

network_df['Latency'] = latencies
network_df['Noise_power'] = noise
network_df['SNR'] = snr
print(network_df)
