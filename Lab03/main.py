import json
import random

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from useful_classes import Network
from useful_classes import SignalInformation
from useful_classes import Connection
from useful_classes import LightPath

# Open and import JSON file
f = open('nodes.json')
nodes_dict = json.load(f)
f.close()
# print(nodes_dict)

# Initialize network DataFrame
# network_df = pd.DataFrame()

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
# Insert paths in network DataFrame as indexes
network_df = pd.DataFrame(index=paths)
# print(network_df)

# Evaluate latency, noise power and SNR for each path
latencies = []
noise = []
snr = []
for path in paths:
    # signal = SignalInformation(path)
    signal = LightPath(1, path)
    network.probe(signal)
    latencies.append(signal.latency)
    noise.append(signal.noise_power)
    snr.append(10*np.log10(signal.signal_power/signal.noise_power))
# Insert latency, noise power and SNR in network DataFrame
network_df['Latency [s]'] = latencies
network_df['Noise_power [W]'] = noise
network_df['SNR [dB]'] = snr
# print(network_df)

# LAB 4 (propagate) + LAB 5 (probe)
# Set weighted_paths attribute
network.weighted_paths = network_df
# LAB 5
# Set route_space attribute
# network.route_space = pd.DataFrame([[line.state for line in network.lines.values()]], index=paths, columns=network.lines)
network.build_route_space()

# 'Channel#' + str(i+1) for i in range(10)]
# for lines in network.lines.values():
#     lines.state = 'free'

# Find the best path for SNR
# path, SNR, ch = network.find_best_snr('A', 'F')
# print("{:.2f}".format(SNR)+'dB', path)

# Find the best path for Latency
# path, Latency = network.find_best_latency('A', 'F')
# print("{:.4f}".format(Latency)+'s', path)

# Build 100 random connections
connections = []
for i in range(100):
    source = random.choice(list(network.nodes.keys()))
    destination = random.choice(list(network.nodes.keys()))
    while source == destination:
        destination = random.choice(list(network.nodes.keys()))
    connection = Connection(source, destination)
    connections.append(connection)

# network.stream(connections)
# lat = [connection.latency for connection in connections if connection.latency != 'None']
# plt.figure()
# plt.hist(lat)                                           # MIGLIORARE PLOT
# plt.title('Latency distribution')
# plt.xticks(rotation=45)
network.stream(connections, parameter='snr')
snr = [connection.snr for connection in connections if connection.snr != 0]
plt.figure()
plt.hist(snr)                                           # MIGLIORARE PLOT
plt.title('SNR distribution')
plt.show()

