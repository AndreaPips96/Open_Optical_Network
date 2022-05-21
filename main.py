import json
import random

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from useful_classes import Network
from useful_classes import Connection
from useful_classes import LightPath
import utils_and_param as up

# Open and import standard JSON file
# f = open('Lab03/nodes.json')
# f = open('Lab07/nodes_full.json')
# f = open('Lab07/nodes_not_full.json')
# f = open('Lab07/nodes_full_fixed_rate.json')
# f = open('Lab07/nodes_full_flex_rate.json')
# f = open('Lab07/nodes_full_shannon.json')

# Open and import personalized JSON file
f = open('288290/network.json')
# f = open('288290/full_network.json')
# f = open('288290/not_full_network.json')
nodes_dict = json.load(f)
f.close()
# print(nodes_dict)

# Initialize network DataFrame
# network_df = pd.DataFrame()

# Build network
network = Network(nodes_dict)
# network.draw()
network.connect()
network.draw(save=False)
exit()
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
    snr.append(up.lin2db(signal.signal_power/signal.noise_power))
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
# connections = []
# for i in range(100):
#     source = random.choice(list(network.nodes.keys()))
#     destination = random.choice(list(network.nodes.keys()))
#     while source == destination:
#         destination = random.choice(list(network.nodes.keys()))
#     connection = Connection(source, destination)
#     connections.append(connection)

# LAB 10 - choose type of simulation
simulation_type = 'network congestion'
# simulation_type = 'single traffic matrix'

# LAB 9
tot_snr = []
tot_avg_snr = []
tot_accepted_Rb = []
tot_avg_Rb = []
tot_capacity_deployed = []
tot_congestion = []
tot_rejections = []
tot_perc_allocations = []
tot_connections = []
legend_param = []
if simulation_type == 'network congestion':
    for M in range(1, up.M_max+1):
        # Generate uniform traffic matrix with M*100Gbps capacity per line
        traffic_matrix = up.generate_traffic_matrix(pd.DataFrame(index=network.nodes.keys(),
                                                                 columns=network.nodes.keys()),
                                                    M)
        # Generate connections and stream them
        connections, congestion = network.manage_traffic_matrix(traffic_matrix)
        # Show progresses
        print('Run '+str(M), f': {congestion}%')
        # Save parameters for future analysis
        tot_snr.append([connection.snr for connection in connections if connection.snr != 0])
        tot_avg_snr.append(sum(tot_snr[M-1]) / len(tot_snr[M-1]))
        tot_accepted_Rb.append([connection.bit_rate / 1e9 for connection in connections if connection.bit_rate != 0])
        tot_avg_Rb.append(sum(tot_accepted_Rb[M-1]) / len(tot_accepted_Rb[M-1]))
        tot_capacity_deployed.append(sum(tot_accepted_Rb[M-1]))
        tot_congestion.append(congestion)
        tot_rejections.append(len(connections) - len(tot_accepted_Rb[M-1]))
        tot_perc_allocations.append(len(tot_accepted_Rb[M-1]) / len(connections) * 100)
        tot_connections.append(len(connections))
        legend_param.append(str(M*100)+'Gbps requests')

    # Plot results
    plt.figure(figsize=(9, 7), dpi=100)
    plt.title('GSNR distribution')
    hist, bins, x = plt.hist(tot_snr, align='mid', bins=20)
    ticks = [(bins[edge] + bins[edge + 1]) / 2 for edge in range(len(bins) - 1)]
    plt.xticks(ticks, rotation=45)
    plt.gca().set_xlabel('GSNR(dB)')
    plt.gca().set_ylabel('Number of connections')
    plt.gca().xaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}'))
    plt.grid(color='gray', which='major', axis='y', linestyle='--')
    plt.gca().set_axisbelow(True)
    plt.legend(legend_param, fontsize='x-small')

    plt.figure(figsize=(9, 7), dpi=100)
    plt.title('Accepted connections Rb')
    if network.nodes['A'].transceiver == 'flex_rate':
        hist1, bins1, x = plt.hist(tot_accepted_Rb, align='mid', bins=4)
        ticks1 = [(bins1[edge] + bins1[edge + 1]) / 2 for edge in range(len(bins1) - 1)]
        plt.xticks(ticks1, [100, 200, 300, 400])
    else:
        hist1, bins1, x = plt.hist(tot_accepted_Rb, align='mid')
        ticks1 = [(bins1[edge] + bins1[edge + 1]) / 2 for edge in range(len(bins1) - 1)]
        plt.xticks(ticks1)
    plt.gca().set_xlabel('Rb(Gbps)')
    plt.gca().set_ylabel('Number of connections')
    plt.grid(color='gray', which='major', axis='y', linestyle='--')
    plt.gca().set_axisbelow(True)
    plt.legend(legend_param, fontsize='x-small')

    fig1, ax1_1 = plt.subplots(figsize=(9, 7), dpi=100)
    ax2_1 = ax1_1.twinx()
    plt.title('Average Rb(M) and GSNR(M) per-line')
    line1, = ax1_1.plot(range(1, up.M_max + 1), tot_avg_Rb, 'b-', label='Rb')
    line2, = ax2_1.plot(range(1, up.M_max + 1), tot_avg_snr, 'r-', label='GSNR')
    ax1_1.set_xlabel('M')
    ax1_1.set_ylabel('Rb(Gbps)')
    ax2_1.set_ylabel('GSNR(dB)')
    # secay = ax2_1.secondary_yaxis('right')
    # secay.set_yticks(np.linspace(25.5, 26.5, 10))
    plt.xticks(range(1, up.M_max + 1))
    # ax1_1.grid(color='gray', which='major', linestyle='--')
    # ax2_1.grid(color='gray', which='major', axis='y', linestyle=':')
    # plt.gca().set_axisbelow(True)
    p = [line1, line2]
    ax1_1.legend(p, [p_.get_label() for p_ in p], loc='lower center')

    fig2, ax1 = plt.subplots(figsize=(9, 7), dpi=100)
    ax2 = ax1.twinx()
    plt.title('Total capacity deployed and network final congestion')
    l1, = ax1.plot(range(1, up.M_max + 1), tot_capacity_deployed, 'b-', label='Capacity')
    l2, = ax2.plot(range(1, up.M_max + 1), tot_congestion, 'r-', label='Congestion')
    ax1.set_xlabel('M')
    ax1.set_ylabel('C(Gbps)')
    ax2.set_ylabel('Network congestion (%)')
    plt.xticks(range(1, up.M_max + 1))
    # ax1.grid(color='gray', which='major', axis='y', linestyle='--')
    # plt.gca().set_axisbelow(True)
    p = [l1, l2]
    ax1.legend(p, [p_.get_label() for p_ in p], loc='lower center')

    plt.figure(figsize=(9, 7), dpi=100)
    plt.title('Connections')
    plt.plot(range(1, up.M_max + 1), tot_connections, 'g--', label='Attempted')
    plt.plot(range(1, up.M_max + 1), [len(tot_accepted_Rb[x]) for x in range(len(tot_accepted_Rb))], 'b-',
             label='Accepted')
    plt.plot(range(1, up.M_max + 1), tot_rejections, 'r-', label='Rejected')
    mean = sum([len(tot_accepted_Rb[x]) for x in range(len(tot_accepted_Rb))]) / len(tot_accepted_Rb)
    plt.axhline(y=mean, color='c', linestyle=':', label='Accepted mean')
    plt.gca().set_xlabel('M')
    plt.gca().set_ylabel('Number of connections')
    plt.annotate('{:.2f}'.format(mean), xy=(1, 2.5+mean))
    plt.xticks(range(1, up.M_max + 1))
    plt.grid(color='gray', which='major', axis='y', linestyle='--')
    plt.gca().set_axisbelow(True)
    plt.legend()

else:
    # Set fixed capacity for uniform traffic matrix
    M = 25
    for m in range(1, up.MC + 1):
        # Generate uniform traffic matrix with M*100Gbps capacity per line
        traffic_matrix = up.generate_traffic_matrix(pd.DataFrame(index=network.nodes.keys(),
                                                                 columns=network.nodes.keys()),
                                                    M)
        # Generate connections and stream them
        connections, congestion = network.manage_traffic_matrix(traffic_matrix)
        # Show progresses
        print('Run '+str(m), f': {congestion}%')
        # Save parameters for future analysis
        tot_snr.append([connection.snr for connection in connections if connection.snr != 0])
        tot_avg_snr.append(sum(tot_snr[m - 1]) / len(tot_snr[m - 1]))
        tot_accepted_Rb.append([connection.bit_rate / 1e9 for connection in connections if connection.bit_rate != 0])
        tot_avg_Rb.append(sum(tot_accepted_Rb[m - 1]) / len(tot_accepted_Rb[m - 1]))
        tot_capacity_deployed.append(sum(tot_accepted_Rb[m - 1]))
        tot_congestion.append(congestion)
        tot_rejections.append(len(connections) - len(tot_accepted_Rb[m - 1]))
        tot_perc_allocations.append(len(tot_accepted_Rb[m - 1]) / len(connections) * 100)
        tot_connections.append(len(connections))
        legend_param.append(f'Run {m}')

    # Plot results
    plt.figure(figsize=(9, 7), dpi=100)
    plt.title('GSNR distribution - M={}'.format(M))
    hist, bins, x = plt.hist(tot_snr, align='mid', bins=20)
    ticks = [(bins[edge] + bins[edge + 1]) / 2 for edge in range(len(bins) - 1)]
    plt.xticks(ticks, rotation=45)
    plt.gca().set_xlabel('GSNR(dB)')
    plt.gca().set_ylabel('Number of connections')
    plt.gca().xaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}'))
    plt.grid(color='gray', which='major', axis='y', linestyle='--')
    plt.gca().set_axisbelow(True)
    plt.legend(legend_param, fontsize='x-small')

    plt.figure(figsize=(9, 7), dpi=100)
    plt.title('Accepted connections Rb - M={}'.format(M))
    if network.nodes['A'].transceiver == 'flex_rate':
        hist1, bins1, x = plt.hist(tot_accepted_Rb, align='mid', bins=4)
        ticks1 = [(bins1[edge] + bins1[edge + 1]) / 2 for edge in range(len(bins1) - 1)]
        plt.xticks(ticks1, [100, 200, 300, 400])
    else:
        hist1, bins1, x = plt.hist(tot_accepted_Rb, align='mid')
        ticks1 = [(bins1[edge] + bins1[edge + 1]) / 2 for edge in range(len(bins1) - 1)]
        plt.xticks(ticks1)
    plt.gca().set_xlabel('Rb(Gbps)')
    plt.gca().set_ylabel('Number of connections')
    plt.grid(color='gray', which='major', axis='y', linestyle='--')
    plt.gca().set_axisbelow(True)
    plt.legend(legend_param, fontsize='x-small')

    fig1, ax1_1 = plt.subplots(figsize=(9, 7), dpi=100)
    ax2_1 = ax1_1.twinx()
    plt.title('Average Rb(M) and GSNR(M) per-line - M={}'.format(M))
    line1, = ax1_1.plot(range(1, up.MC + 1), tot_avg_Rb, 'b-', label='Rb')
    line2, = ax2_1.plot(range(1, up.MC + 1), tot_avg_snr, 'r-', label='GSNR')
    ax1_1.set_xlabel('Monte Carlo runs')
    ax1_1.set_ylabel('Rb(Gbps)')
    ax2_1.set_ylabel('GSNR(dB)')
    # secay = ax2_1.secondary_yaxis('right')
    # secay.set_yticks(np.arange(25, 27.5, 0.1))
    plt.xticks(range(1, up.MC + 1))
    # ax1_1.grid(color='gray', which='major', linestyle='--')
    # ax2_1.grid(color='gray', which='major', axis='y', linestyle=':')
    # plt.gca().set_axisbelow(True)
    p = [line1, line2]
    ax1_1.legend(p, [p_.get_label() for p_ in p], loc='lower center')

    fig2, ax1 = plt.subplots(figsize=(9, 7), dpi=100)
    ax2 = ax1.twinx()
    plt.title('Total capacity deployed and network final congestion')
    l1, = ax1.plot(range(1, up.MC + 1), tot_capacity_deployed, 'b-', label='Capacity')
    l2, = ax2.plot(range(1, up.MC + 1), tot_congestion, 'r-', label='Congestion')
    ax1.set_xlabel('Monte Carlo runs')
    ax1.set_ylabel('C(Gbps)')
    ax2.set_ylabel('Network congestion (%)')
    plt.xticks(range(1, up.MC + 1))
    # ax1.grid(color='gray', which='major', linestyle='--')
    # plt.gca().set_axisbelow(True)
    p = [l1, l2]
    ax1.legend(p, [p_.get_label() for p_ in p], loc='lower center')

    plt.figure(figsize=(9, 7), dpi=100)
    plt.title('Connections')
    plt.plot(range(1, up.MC + 1), tot_connections, 'g--', label='Attempted')
    plt.plot(range(1, up.MC + 1), [len(tot_accepted_Rb[x]) for x in range(len(tot_accepted_Rb))], 'b-',
             label='Accepted')
    plt.plot(range(1, up.MC + 1), tot_rejections, 'r-', label='Rejected')
    mean = sum([len(tot_accepted_Rb[x]) for x in range(len(tot_accepted_Rb))]) / len(tot_accepted_Rb)
    plt.axhline(y=mean, color='c', linestyle=':', label='Accepted mean')
    plt.gca().set_xlabel('Monte Carlo runs')
    plt.gca().set_ylabel('Number of connections')
    plt.annotate('{:.2f}'.format(mean), xy=(1, 2.5 + mean))
    plt.xticks(range(1, up.MC + 1))
    plt.grid(color='gray', which='major', axis='y', linestyle='--')
    plt.gca().set_axisbelow(True)
    plt.legend()
# [connection.snr for connection in connections if connection.snr != 0]
# network.stream(connections, 'latency')
# lat = [connection.latency for connection in connections if connection.latency != 'None']
# plt.figure()
# plt.hist(lat)                                           # MIGLIORARE PLOT
# plt.title('Latency distribution')
# plt.xticks(rotation=45)

# network.stream(connections, 'snr')
# snr = [connection.snr for connection in connections if connection.snr != 0]

plt.show()
print()
exit()

bit_rates = [connection.bit_rate for connection in connections if connection.bit_rate != 0]
print(len(bit_rates))
avg_bit_rate = np.mean(bit_rates)
print('Average deployed bit rate: ' + str(avg_bit_rate/1e9) + 'Gbps')
tot_capacity = np.sum(bit_rates)
print('Total deployed capacity: ' + str(tot_capacity/1e9) + 'Gbps')
plt.figure()
plt.hist(bit_rates)                                           # MIGLIORARE PLOT
plt.title('Bit rate allocation distribution')
plt.xticks(rotation=45)

plt.show()

# FORMULA P_opt DA MODIFICARE TOGLIENDO Bn? - V
# SCRIVERE FUNZIONE PER GESTIRE TRAFFIC MATRIX E CONNESSIONI
# IMPOSTARE MONTE CARLO
# number of 0s in switching matrix divided by Nch X100 is the congestion percentage


