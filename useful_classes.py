# USEFUL CLASSES
import logging
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from copy import deepcopy
import utils_and_param as up

logging.basicConfig(filename='network.txt', level=logging.INFO, filemode='w')
# free = 1
# occupied = 0


class SignalInformation:

    def __init__(self, path):
        self.signal_power = 1.0e-03  # float
        self.noise_power = 0.0  # float
        self.latency = 0.0  # float
        self.path = path  # list[string]

    def update_powlat(self, s_power, n_power, latency):
        # update powers and latency
        self.signal_power += s_power
        self.noise_power += n_power
        self.latency += latency
        return self.signal_power, self.noise_power, self.latency

    def update_path(self):
        # remove first element of the list
        self.path = self.path[1:]
        # return self.path


class Node:

    def __init__(self, label, dictionary):
        self.label = label                                      # string
        self.position = dictionary['position']                  # tuple(float, float)
        self.connected_nodes = dictionary['connected_nodes']    # list[string]
        self.successive = {}                                    # dict[Line]
        self.switching_matrix = None                            # LAB 6 - dict[dict[]]
        if 'transceiver' in dictionary.keys():                  # LAB 7 - string
            self.transceiver = dictionary['transceiver']
        else:
            self.transceiver = 'fixed_rate'

    def propagate(self, lightpath, dynamic_sw):
        if not dynamic_sw:
            if len(lightpath.path) > 1:
                next_line = self.successive[self.label + lightpath.path[1]]
                lightpath.signal_power = next_line.optimized_launch_power()
                lightpath.update_path()
                # call the successive element propagate method, accordingly to the specified path.
                self.successive[next_line.label].propagate(lightpath, dynamic_sw)
        else:
            # LAB 9
            # check for last node not reached
            if len(lightpath.path) > 1:
                # LAB 7
                # set side channel occupancy
                if len(lightpath.path) > 2:
                    if lightpath.channel+1 < 10:
                        self.successive[lightpath.path[:2]].successive[lightpath.path[1]] \
                            .switching_matrix[lightpath.path[0]][lightpath.path[2]][lightpath.channel+1] = up.OCCUPIED
                    if lightpath.channel-1 >= 0:
                        self.successive[lightpath.path[:2]].successive[lightpath.path[1]] \
                            .switching_matrix[lightpath.path[0]][lightpath.path[2]][lightpath.channel-1] = up.OCCUPIED
                    self.successive[lightpath.path[:2]].successive[lightpath.path[1]] \
                        .switching_matrix[lightpath.path[0]][lightpath.path[2]][lightpath.channel] = up.OCCUPIED

                next_line = self.successive[self.label + lightpath.path[1]]
                lightpath.signal_power = next_line.optimized_launch_power()
                lightpath.update_path()
                # call the successive element propagate method, accordingly to the specified path.
                self.successive[next_line.label].propagate(lightpath, dynamic_sw)
                # if lightpath.path != '':
                #     call the successive element propagate method, accordingly to the specified path.
                #     next_label = lightpath.path[0]
                #     self.successive[self.label + next_label].propagate(lightpath)

    # LAB 5
    def probe(self, lightpath):
        if len(lightpath.path) > 1:
            next_line = self.successive[self.label + lightpath.path[1]]
            lightpath.signal_power = next_line.optimized_launch_power()
            lightpath.update_path()
            # call the successive element propagate method, accordingly to the specified path.
            self.successive[next_line.label].probe(lightpath)

        # lightpath.update_path()
        # if lightpath.path != '':
        #     # call the successive element probe method, accordingly to the specified path.
        #     next_label = lightpath.path[0]
        #     self.successive[self.label + next_label].probe(lightpath)


class Line:

    def __init__(self, label, length):
        self.label = label  # string
        self.length = length  # float
        self.successive = {}  # dict[]
        self.state = np.array([up.FREE] * 10)  # string - LAB 4 - LAB 5 - LAB 6
        self.n_amplifiers = 1 + np.ceil(self.length/up.DIST_BTW_AMP)    # LAB 8
        self.n_span = self.n_amplifiers - 1
        self.amp_gain = up.db2lin(up.AMP_GAIN)    # linear units
        self.amp_nf = up.db2lin(up.AMP_NF)        # linear units
        self.alpha_db = up.ALPHA_dB
        self.alpha_lin = up.alpha_db2lin(self.alpha_db) * 1e-3      # 1/m
        self.beta_2 = up.BETA_2
        self.gamma = up.GAMMA

    def latency_generation(self):
        return self.length / ((2 / 3) * up.c)

    def noise_generation(self, lightpath):
        # return 1e-9 * signal_power * self.length
        # LAB 9
        # print('ASE: '+str(self.ase_generation())+' NLI: '+str(self.nli_generation(lightpath)))  # DEBUG
        # pnli = self.nli_generation(lightpath)       # DEBUG
        return self.ase_generation() + self.nli_generation(lightpath)

    def propagate(self, lightpath, dynamic_sw):
        """
            Method to propagate a lightpath on all lines along a path
        """
        # Update power, noise and latency added by the line
        lightpath.update_powlat(0, self.noise_generation(lightpath), self.latency_generation())
        # Set line status to occupied then propagate signal - LAB 4
        self.state[lightpath.channel] = up.OCCUPIED  # LAB 5
        next_label = lightpath.path[0]
        self.successive[next_label].propagate(lightpath, dynamic_sw)

    # LAB 5
    def probe(self, lightpath):
        """
            Method to propagate a lightpath on all lines along a path without occupying them
        """
        # Update power, noise and latency added by the line
        lightpath.update_powlat(0, self.noise_generation(lightpath), self.latency_generation())
        # Set next line
        next_label = lightpath.path[0]
        self.successive[next_label].probe(lightpath)

    # LAB 8
    def ase_generation(self):
        """
        evaluates the total amount of amplified spontaneous emissions (ASE) in linear units generated by the amplifiers
        supposing that a cascade of amplifiers introduces a noise amount which follows the expression:
        ASE = N (hf Bn NF [G ??? 1])
        where N is the number of amplifiers, h is the Plank constant, f is the frequency which would be fixed to
        193.414 THz (C-band center), Bn is the noise bandwidth fixed to 12.5 GHz, N F and G are the amplifier noise
        figure and gain, respectively.
        :return: total ASE in linear units
        """
        ase = self.n_amplifiers * (up.h_plank * up.CENTER_F * up.Bn * self.amp_nf * (self.amp_gain-1))
        return ase

    def nli_generation(self, lightpath):
        """
        evaluates the total amount generated by the nonlinear interface noise using the formula (in linear units):
        NLI = P * ch3 * ??_nli * N_span
        :return: NLI in linear units
        """
        eta_nli = up.eta_nli_eval(self.alpha_lin, self.beta_2, self.gamma, len(self.state))
        return (lightpath.signal_power**3) * eta_nli * self.n_span * up.Bn

    # LAB 9
    def optimized_launch_power(self):
        """
        determination of the optimal launch power using Local Optimization Global Optimization (LOGO) strategy
        :return: optimal launch power
        """
        P_ase = self.ase_generation()
        eta_nli = up.eta_nli_eval(self.alpha_lin, self.beta_2, self.gamma, len(self.state))
        return np.cbrt(P_ase / (2*eta_nli*self.n_span*up.Bn))   # *Bn


class Network:

    def __init__(self, my_dict):
        self.nodes = {}
        self.lines = {}
        self.weighted_paths = pd.DataFrame()
        self.route_space = pd.DataFrame()
        self.default_switching_matrices = {}
        self.cnt = 0

        for key in my_dict:
            self.nodes[key] = Node(key, my_dict[key])

            # LAB7
            # if 'switching_matrix' in my_dict[key].keys():
            self.default_switching_matrices[key] = my_dict[key]['switching_matrix']
            # easier way to build the switching matrix BUT needs np.array() before multiplication taken
            # self.nodes[key].switching_matrix = np.array(my_dict[key]['switching_matrix'])
            first = True
            for con_node in my_dict[key]['switching_matrix']:
                if first:
                    first = False
                    self.nodes[key].switching_matrix = self.build_switching_matrix(key, con_node, my_dict)
                else:
                    self.nodes[key].switching_matrix.update(self.build_switching_matrix(key, con_node, my_dict))
            #

            for element in self.nodes[key].connected_nodes:
                line_label = (key + element)
                pos = np.array(self.nodes[key].position)
                next_pos = np.array(my_dict[element]['position'])
                distance = np.sqrt(np.sum((pos - next_pos) ** 2))

                self.lines[line_label] = Line(line_label, distance)

    def connect(self):
        for label in self.nodes:
            node = self.nodes[label]
            # first = True
            for con_node in node.connected_nodes:
                con_line = node.label + con_node
                node.successive[con_line] = self.lines[con_line]
                # if first:
                #     first = False
                #     node.switching_matrix = self.build_switching_matrix(label, con_node)
                # else:
                #     node.switching_matrix.update(self.build_switching_matrix(label, con_node))

        for label in self.lines:
            line = self.lines[label]
            line.successive[line.label[0]] = self.nodes[line.label[0]]
            line.successive[line.label[1]] = self.nodes[line.label[1]]

    def find_paths(self, node1, node2):
        """
            Given two node labels, this function returns all the paths that connect the two nodes
            as list of node labels.
            The admissible paths have to cross any node at most once.
        """
        available_path = []
        for i in range(len(self.nodes.keys()) - 1):
            if i == 0:
                possible_paths = self.generate(node1, self.nodes[node1].connected_nodes)
                copy_possible_paths = possible_paths
                for path in copy_possible_paths:
                    if path[-1] not in self.nodes[node1].connected_nodes:
                        possible_paths.remove(path)
                    elif path[-1] == node2:
                        available_path.append(path)
            else:
                elem = range(len(possible_paths))
                for j in elem:
                    derived_paths = self.generate(possible_paths[0], self.nodes[possible_paths[0][-1]].connected_nodes)
                    for path in derived_paths:
                        aaa = path[-1]
                        aab = path[-2]
                        aac = self.nodes[path[-2]].connected_nodes
                        if path[-1] not in self.nodes[path[-2]].connected_nodes:
                            derived_paths.remove(path)
                        elif path[-1] == node2:
                            available_path.append(path)
                            derived_paths.remove(path)
                    possible_paths.pop(0)
                    possible_paths += derived_paths
        return available_path

    def generate(self, string1, labels):
        out = []
        for letter in labels:
            if letter not in string1:
                out.append(string1 + letter)
        return out

    def propagate(self, lightpath, dynamic_sw):
        """
            This function has to propagate the signal information through the path specified in it
            and returns the modified spectral information.
        """
        node = self.nodes[lightpath.path[0]]
        node.propagate(lightpath, dynamic_sw)

    def draw(self, save=False):
        """
            This function draws the network using matplotlib
            (nodes as dots and connection as lines).
        """
        fig = plt.figure(figsize=(9, 7), dpi=100)
        for label in self.nodes:
            node = self.nodes[label]
            x0 = node.position[0]
            y0 = node.position[1]
            plt.plot(x0, y0, 'ro', markersize=20, zorder=5)
            plt.text(x0, y0, label, fontsize=12, fontweight='semibold', zorder=10,
                     horizontalalignment='center', verticalalignment='center')
            for connected_node_label in node.connected_nodes:
                n1 = self.nodes[connected_node_label]
                x1 = n1.position[0]
                y1 = n1.position[1]
                plt.plot([x0, x1], [y0, y1], 'b', zorder=0, linewidth=2)
        plt.title('Network topology')
        plt.xlabel('Distance (m)')
        plt.xlabel('Distance (m)')
        plt.ticklabel_format(axis='both', style='sci', scilimits=(3, 3), useMathText=True)
        if save:
            fig.savefig('Network_topology.png')
        # plt.show()

    # LAB 4
    def find_best_snr(self, snode, dnode):
        best_snr = 0
        best_path = ''
        ch = 0
        # Scan all available paths
        for path in self.weighted_paths.index:
            there_is_space = True
            # Make computations only if source and destination nodes match
            if path[0] == snode and path[-1] == dnode:
                # Check path's lines status
                for i in range(len(path) - 1):
                    if up.FREE not in self.lines[path[i] + path[i + 1]].state:
                        # First totally occupied line makes all path unfeasible
                        there_is_space = False
                        break
                    # if self.lines[path[i]+path[i+1]].state != FREE:
                    #     # First occupied line makes all path unfeasible
                    #     FREE = False
                    #     break
                # FREE, ch = find_ch(path)
                if self.weighted_paths.loc[path, 'SNR [dB]'] > best_snr and there_is_space:
                    ch = self.find_ch(path)
                    if ch != 0:
                        best_snr = self.weighted_paths.loc[path, 'SNR [dB]']
                        best_path = path
        return best_path, best_snr, ch

    def find_best_latency(self, snode, dnode):
        best_lat = 1000
        best_path = ''
        ch = 0
        # Scan all available paths
        for path in self.weighted_paths.index:
            there_is_space = True
            # Make computations only if source and destination nodes match
            if path[0] == snode and path[-1] == dnode:
                # Check path's lines status
                for i in range(len(path) - 1):
                    if up.FREE not in self.lines[path[i] + path[i + 1]].state:
                        # First totally occupied line makes all path unfeasible
                        there_is_space = False
                        break
                    # if self.lines[path[i]+path[i+1]].state != FREE:
                    #     # First occupied line makes all path unfeasible
                    #     FREE = False
                    #     break
                if self.weighted_paths.loc[path, 'Latency [s]'] < best_lat and there_is_space:
                    ch = self.find_ch(path)
                    if ch != 0:
                        best_lat = self.weighted_paths.loc[path, 'Latency [s]']
                        best_path = path
        return best_path, best_lat, ch

    def stream(self, connection, parameter='latency'):
        # i = 1
        # for connection in connections:
        if parameter == 'latency':
            path, best_lat, channel = self.find_best_latency(connection.input, connection.output)
        elif parameter == 'snr':
            path, best_snr, channel = self.find_best_snr(connection.input, connection.output)
        else:
            raise NameError('Wrong parameter: nor \'latency\' nor \'snr\' inserted')
        if path != '':
            # LAB 9
            if len(path) > 2:
                self.cnt += 1
            # print(path)
            signal = LightPath(channel - 1, path)
            bit_rate = self.calculate_bit_rate(signal, self.nodes[path[0]].transceiver)
            connection.bit_rate = bit_rate
            if bit_rate > 0:
                # print(path, channel)
                # i = i + 1
                # signal = LightPath(channel - 1, path)
                self.propagate(signal, up.dynamic_sw)
                if parameter == 'latency':
                    connection.latency = best_lat
                    # connection.snr = 10 * np.log10(signal.signal_power / signal.noise_power)
                    connection.snr = up.lin2db(signal.signal_power / signal.noise_power)
                    connection.signal_power = signal.signal_power
                else:
                    connection.latency = signal.latency
                    # connection.snr = 10 * np.log10(signal.signal_power / signal.noise_power)
                    # connection.snr = best_snr
                    connection.snr = up.lin2db(signal.signal_power / signal.noise_power)
                    connection.signal_power = signal.signal_power
                self.update_route_space(path)
            else:
                connection.latency = 'None'
                connection.snr = 0
        else:
            connection.latency = 'None'
            connection.snr = 0

        # for node in self.nodes:
        #     self.nodes[node].switching_matrix = dict(self.default_switching_matrices[node])
        # for line in self.lines:
        #     self.lines[line].state = np.array([FREE] * 10)

        # for connection in connections:
        #     if parameter == 'latency':
        #         path, best_lat, channel = self.find_best_latency(connection.input, connection.output)
        #         if path == '' and best_lat == 1000:
        #             connection.latency = 'None'
        #             connection.snr = 0
        #         else:
        #             print(path, best_lat, channel, i)
        #             i = i + 1
        #             signal = LightPath(channel - 1, path)
        #             self.propagate(signal)
        #             connection.latency = signal.latency
        #             connection.snr = 10 * np.log10(signal.signal_power / signal.noise_power)
        #             self.update_route_space(path)
        #     elif parameter == 'snr':
        #         path, best_snr, channel = self.find_best_snr(connection.input, connection.output)
        #         if (path == '' and best_snr == 0) or channel == 0:
        #             connection.latency = 'None'
        #             connection.snr = 0
        #         else:
        #             print(path, best_snr, channel, i)
        #             i = i+1
        #             bit_rate = self.calculate_bit_rate(path, self.nodes[path[0]].transceiver)
        #             connection.bit_rate = bit_rate
        #             if bit_rate > 0:
        #                 signal = LightPath(channel - 1, path)
        #                 self.propagate(signal)
        #                 connection.latency = signal.latency
        #                 # connection.snr = 10 * np.log10(signal.signal_power / signal.noise_power)
        #                 connection.snr = best_snr
        #                 self.update_route_space(path)
        #     else:
        #         raise NameError('Wrong parameter: nor \'latency\' nor \'snr\' inserted')

    # LAB 5
    def probe(self, lightpath):
        """
            This function propagates the lightpath information through the path specified in it.
        """
        node = self.nodes[lightpath.path[0]]
        node.probe(lightpath)

    def build_route_space(self):
        route_space = pd.DataFrame(index=self.weighted_paths.index, columns=self.lines)
        for line in self.lines.values():
            for path in self.weighted_paths.index:
                if line.label in path:
                    route_space.loc[path][line.label] = deepcopy(line.state)
        self.route_space = route_space

    def update_route_space(self, path):
        # line = path[0]
        # for i in path[1:]:
        #     line += i
        #     for route in self.route_space.index:
        #         if line in route:
        #             self.route_space.loc[route][line] = deepcopy(self.lines[line].state)
        #             # linea sotto sbagliata ma per reference
        #             # self.route_space.loc[route][line] = self.lines[line].state * \
        #             #                                     self.nodes[i].switching_matrix[line[0]][line[1]]    # LAB 6
        #     line = i
        if len(path) < 3:
            line = path
            for route in self.route_space.index:
                if line in route:
                    self.route_space.loc[route][line] = np.multiply(self.route_space.loc[route][line],
                                                                    self.lines[line].state)
        else:
            for i in list(range(1, len(path)-1)):
                for j in range(2):
                    line = path[i-(1-j): i+(j+1)]
                    # print(path[i - 1], path[i + 1], '\t'+line)
                    for route in self.route_space.index:
                        if line in route:
                            # LAB 6
                            self.route_space.loc[route][line] = \
                                np.multiply(self.lines[line].state,
                                            self.nodes[path[i]].switching_matrix[path[i-1]][path[i+1]],
                                            self.route_space.loc[route][line])

    def find_ch(self, path):
        row = self.route_space.loc[[path]]
        notnull_col = []
        free_indices = []
        for col in row:
            if not row[col].isnull().values.any():
                notnull_col.append(col)
                free_indices.append([i + 1 for i, x in enumerate(row[col].values.any()) if x == up.FREE])
        # common_index = set(free_indices[0])
        # for idx in free_indices[1:]:
        #     common_index.intersection_update(set(idx))
        common_index = set(free_indices[0]).intersection(*free_indices)
        if len(common_index) == 0:
            return 0
        else:
            return min(common_index)

    # LAB 6
    def build_switching_matrix(self, node, label1, my_dict):
        # switching_matrix = {}
        # switching_matrix[label1] = {}
        # for label2 in self.nodes[node].connected_nodes:
        #     # if label1 == label2:
        #     # LAB7
        #     if 0 in my_dict[node]['switching_matrix'][label1][label2]:
        #         switching_matrix[label1][label2] = np.array([up.OCCUPIED] * up.Nch)
        #     else:
        #         switching_matrix[label1][label2] = np.array([up.FREE] * up.Nch)
        switching_matrix = deepcopy(dict(self.default_switching_matrices[node]))
        return switching_matrix

    # LAB 7 - LAB 9
    def calculate_bit_rate(self, lightpath, strategy):
        if strategy == 'fixed_rate':
            bit_rate = up.fixed_bit_rate(up.db2lin(self.weighted_paths.loc[lightpath.path, 'SNR [dB]']),
                                         lightpath.symbol_rate)
        elif strategy == 'flex_rate':
            bit_rate = up.flex_bit_rate(up.db2lin(self.weighted_paths.loc[lightpath.path, 'SNR [dB]']),
                                        lightpath.symbol_rate)
        elif strategy == 'shannon':
            bit_rate = up.shannon_bit_rate(up.db2lin(self.weighted_paths.loc[lightpath.path, 'SNR [dB]']),
                                           lightpath.symbol_rate)
        else:
            raise NameError('Wrong strategy: nor \'fixed_rate\' nor \'flex_rate\' nor \'shannon\' inserted')
        return bit_rate

    # LAB 9
    def manage_traffic_matrix(self, traffic_matrix):
        MAX_REJ = 15.0
        rejection_cnt = 0
        rejection_perc = 0.0
        congestion_percentage = 0.0
        connections = []
        non_zero_request = []
        # In order to track easily if traffic matrix is null save all possible in-out nodes and delete them when traffic
        # matrix gets to 0 for that in-out couple
        for source in self.nodes.keys():
            for destination in self.nodes.keys():
                if source != destination:
                    non_zero_request.append(source + destination)
        # Create new connections until either the traffic matrix is null, the network is saturated or too many
        # consecutive blocking events
        # while not congested and not null matrix:
        while (int(congestion_percentage) < 100) and non_zero_request and rejection_perc <= MAX_REJ:
            # Choose a new random connection among available ones
            nodes = random.choice(non_zero_request)
            source = nodes[0]
            destination = nodes[1]

            # Make new connection
            connection = Connection(source, destination)
            # Add the new connection to the list collecting all connections
            connections.append(connection)
            # Stream new connection
            self.stream(connection)

            # If connection wasn't rejected update traffic matrix and congestion
            if connection.snr != 0 and connection.latency != 'None':
                if traffic_matrix[source][destination] - connection.bit_rate > 0:
                    traffic_matrix[source][destination] -= connection.bit_rate
                elif traffic_matrix[source][destination] - connection.bit_rate == 0:
                    traffic_matrix[source][destination] -= connection.bit_rate
                    non_zero_request.remove(nodes)
                else:
                    connection.bit_rate = traffic_matrix[source][destination]
                    traffic_matrix[source][destination] = 0
                    non_zero_request.remove(nodes)
                congestion_percentage = up.congestion_eval(self)
                # print(congestion_percentage)
            # If connection was rejected count rejections: if more than 15% exit because of too many rejections
            else:
                rejection_cnt += 1
                rejection_perc = rejection_cnt/len(connections)*100

        info = str(congestion_percentage) + ' [' + ''.join(x for x in non_zero_request) + ']'
        unavailable_ch = 0
        available_ch = 0
        for line in self.lines.keys():
            unavailable_ch += np.count_nonzero(self.lines[line].state == up.OCCUPIED)
            available_ch += np.sum(self.lines[line].state)
        lines = '0s:' + str(unavailable_ch) + ' ' + '1s:' + str(available_ch) + ' - Paths>2: ' + str(self.cnt)
        logging.info(info)
        logging.info(lines)
        # print(f'{congestion_percentage}%'

        return connections, congestion_percentage

    def restore(self):
        # Reset network for future experiments
        for node in self.nodes:
            self.nodes[node].switching_matrix = deepcopy(dict(self.default_switching_matrices[node]))
        for line in self.lines:
            self.lines[line].state = np.array([up.FREE] * 10)
        self.build_route_space()
        return


class Connection:

    def __init__(self, snode, dnode):
        self.input = snode              # string
        self.output = dnode             # string
        self.signal_power = 1.0e-03     # float
        self.latency = 0.0              # float
        self.snr = 0.0                  # float
        self.bit_rate = 0.0             # LAB 7 - float


# LAB 5
class LightPath(SignalInformation):

    def __init__(self, slot, path):
        SignalInformation.__init__(self, path)
        self.channel = slot         # integer
        self.symbol_rate = up.Rs
        self.df = up.DELTA_F
        # super().__init__(slot)
