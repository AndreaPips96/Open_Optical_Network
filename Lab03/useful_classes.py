# USEFUL CLASSES
import scipy.constants as sp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from copy import deepcopy

free = 1
occupied = 0


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
        self.label = label  # string
        self.position = dictionary["position"]  # tuple(float, float)
        self.connected_nodes = dictionary["connected_nodes"]  # list[string]
        self.successive = {}  # dict[Line]
        self.switching_matrix = None  # LAB 6 - dict[dict[]]

    def propagate(self, lightpath):
        lightpath.update_path()
        if lightpath.path != '':
            # call the successive element propagate method, accordingly to the specified path.
            next_label = lightpath.path[0]
            self.successive[self.label + next_label].propagate(lightpath)

    # LAB 5
    def probe(self, lightpath):
        lightpath.update_path()
        if lightpath.path != '':
            # call the successive element probe method, accordingly to the specified path.
            next_label = lightpath.path[0]
            self.successive[self.label + next_label].probe(lightpath)


class Line:

    def __init__(self, label, length):
        self.label = label  # string
        self.length = length  # float
        self.successive = {}  # dict[]
        self.state = np.array([free] * 10)  # string - LAB 4 - LAB 5 - LAB 6

    def latency_generation(self):
        return self.length / ((2 / 3) * sp.speed_of_light)

    def noise_generation(self, signal_power):
        return 1e-9 * signal_power * self.length

    def propagate(self, lightpath):
        """
            Method to propagate a lightpath on all lines along a path
        """
        # Update power, noise and latency added by the line
        lightpath.update_powlat(0, self.noise_generation(lightpath.signal_power), self.latency_generation())
        # Set line status to occupied then propagate signal - LAB 4
        self.state[lightpath.channel] = occupied  # LAB 5
        next_label = lightpath.path[0]
        self.successive[next_label].propagate(lightpath)

    # LAB 5
    def probe(self, lightpath):
        """
            Method to propagate a lightpath on all lines along a path without occupying them
        """
        # Update power, noise and latency added by the line
        lightpath.update_powlat(0, self.noise_generation(lightpath.signal_power), self.latency_generation())
        # Set next line
        next_label = lightpath.path[0]
        self.successive[next_label].probe(lightpath)


class Network:

    def __init__(self, my_dict):
        self.nodes = {}
        self.lines = {}
        self.weighted_paths = pd.DataFrame()
        self.route_space = pd.DataFrame()

        for key in my_dict:
            self.nodes[key] = Node(key, my_dict[key])

            for element in self.nodes[key].connected_nodes:
                line_label = (key + element)
                pos = np.array(self.nodes[key].position)
                next_pos = np.array(my_dict[element]["position"])
                distance = np.sqrt(np.sum((pos - next_pos) ** 2))

                self.lines[line_label] = Line(line_label, distance)

    def connect(self):
        for label in self.nodes:
            node = self.nodes[label]
            first = True
            for con_node in node.connected_nodes:
                con_line = node.label + con_node
                node.successive[con_line] = self.lines[con_line]
                if first:
                    first = False
                    node.switching_matrix = self.build_switching_matrix(label, con_node)
                else:
                    node.switching_matrix.update(self.build_switching_matrix(label, con_node))

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

    def propagate(self, lightpath):
        """
            This function has to propagate the signal information through the path specified in it
            and returns the modified spectral information.
        """
        node = self.nodes[lightpath.path[0]]
        node.propagate(lightpath)

    def draw(self):
        """
            This function has to draw the network using matplotlib
            (nodes as dots and connection as lines).
        """
        fig = plt.figure()
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
        fig.savefig('Network_topology.png')
        plt.show()

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
                    if free not in self.lines[path[i] + path[i + 1]].state:
                        # First totally occupied line makes all path unfeasible
                        there_is_space = False
                        break
                    # if self.lines[path[i]+path[i+1]].state != free:
                    #     # First occupied line makes all path unfeasible
                    #     free = False
                    #     break
                # free, ch = find_ch(path)
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
                    if free not in self.lines[path[i] + path[i + 1]].state:
                        # First totally occupied line makes all path unfeasible
                        there_is_space = False
                        break
                    # if self.lines[path[i]+path[i+1]].state != free:
                    #     # First occupied line makes all path unfeasible
                    #     free = False
                    #     break
                if self.weighted_paths.loc[path, 'Latency [s]'] < best_lat and there_is_space:
                    ch = self.find_ch(path)
                    if ch != 0:
                        best_lat = self.weighted_paths.loc[path, 'Latency [s]']
                        best_path = path
        return best_path, best_lat, ch

    def stream(self, connections, parameter='latency'):
        i = 1
        for connection in connections:
            if parameter == 'latency':
                path, best_lat, channel = self.find_best_latency(connection.input, connection.output)
                if path == '' and best_lat == 1000:
                    connection.latency = 'None'
                    connection.snr = 0
                else:
                    print(path, best_lat, channel)
                    signal = LightPath(channel - 1, path)
                    self.propagate(signal)
                    connection.latency = signal.latency
                    connection.snr = 10 * np.log10(signal.signal_power / signal.noise_power)
                    self.update_route_space(path)
            elif parameter == 'snr':
                path, best_snr, channel = self.find_best_snr(connection.input, connection.output)
                if (path == '' and best_snr == 0) or channel == 0:
                    connection.latency = 'None'
                    connection.snr = 0
                else:
                    print(path, best_snr, channel, i)
                    i = i+1
                    signal = LightPath(channel - 1, path)
                    self.propagate(signal)
                    connection.latency = signal.latency
                    connection.snr = 10 * np.log10(signal.signal_power / signal.noise_power)
                    self.update_route_space(path)
            else:
                raise NameError('Wrong parameter: nor \'latency\' nor \'snr\' inserted')

    # LAB 5
    def probe(self, lightpath):
        """
            This function has to propagate the lightpath information through the path specified in it
            and returns the modified spectral information.
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
            for route in self.route_space.index:
                if path in route:
                    self.route_space.loc[route][path] = deepcopy(self.lines[path].state)
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
                                            self.nodes[path[i]].switching_matrix[path[i-1]][path[i+1]])

    def find_ch(self, path):
        row = self.route_space.loc[[path]]
        notnull_col = []
        free_indices = []
        for col in row:
            if not row[col].isnull().values.any():
                notnull_col.append(col)
                free_indices.append([i + 1 for i, x in enumerate(row[col].values.any()) if x == free])
        # common_index = set(free_indices[0])
        # for idx in free_indices[1:]:
        #     common_index.intersection_update(set(idx))
        common_index = set(free_indices[0]).intersection(*free_indices)
        if len(common_index) == 0:
            return 0
        else:
            return min(common_index)

    # LAB 6
    def build_switching_matrix(self, node, label1):
        switching_matrix = {}
        switching_matrix[label1] = {}
        for label2 in self.nodes[node].connected_nodes:
            if label1 == label2:
                switching_matrix[label1][label2] = np.array([occupied] * 10)
            else:
                switching_matrix[label1][label2] = np.array([free] * 10)
        return switching_matrix


class Connection:

    def __init__(self, snode, dnode):
        self.input = snode  # string
        self.output = dnode  # string
        self.signal_power = 1.0e-03  # float
        self.latency = 0.0  # float
        self.snr = 0.0  # float


# LAB 5
class LightPath(SignalInformation):

    def __init__(self, slot, path):
        SignalInformation.__init__(self, path)
        self.channel = slot  # integer
        # super().__init__(slot)
