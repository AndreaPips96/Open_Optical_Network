# USEFUL CLASSES
import scipy.constants as sp
import numpy as np
import matplotlib.pyplot as plt

class SignalInformation:

    def __init__(self, path):
        self.signal_power = 1.0                     # float
        self.noise_power = 0.0                      # float
        self.latency = 0.0                          # float
        self.path = path                            # list[string]

    def update_powlat(self, s_power, n_power, latency):
        # update powers and latency
        self.signal_power += s_power
        self.noise_power += n_power
        self.latency += latency
        return self.signal_power, self.noise_power, self.latency

    def update_path(self, path):
        # remove first element of the list
        self.path = self.path.pop(0)
        return self.path

class Node:

    def __init__(self, label, dictionary):
        self.label = label                                      # string
        self.position = dictionary["position"]                  # tuple(float, float)
        self.connected_nodes = dictionary["connected_nodes"]    # list[string]
        self.successive = {}                                    # dict[Line]

    def propagate(self, signal_info):
        signal_info.update_path()

        # call the successive element propagate method,
        # accordingly to the specified path.
        next_label = signal_info.path[0]
        self.successive[self.label + next_label].propagate(signal_info)



class Line:

    def __init__(self, label, length):
        self.label = label          # string
        self.length = length        # float
        self.successive = {}        # dict[]

    def latency_generation(self):
        return (2/3)*sp.speed_of_light*self.length

    def noise_generation(self, signal_power):
        return 1e-9*signal_power*self.length

    def propagate(self, signal_info):
        signal_info.update_powlat(0, self.noise_generation(signal_info.signal_power), self.latency_generation())

        next_label = signal_info.path[0]
        self.successive[next_label].propagate(signal_info)


class Network:

    def __init__(self, my_dict):
        self.nodes = {}
        self.lines = {}

        for key in my_dict:
            self.nodes[key] = Node(key, my_dict[key])

            for element in self.nodes[key].connected_nodes:
                line_label = (key + element)
                pos = np.array(self.nodes[key].position)
                next_pos = np.array(my_dict[element]["position"])
                distance = np.sqrt(np.sum(pos - next_pos)**2)

                self.lines[line_label] = Line(line_label, distance)


    def connect(self):
        for label in self.nodes:
            node = self.nodes[label]
            for con_node in node.connected_nodes:
                con_line = node.label + con_node
                node.successive[con_line] = self.lines[con_line]

        for label in self.lines:
            line = self.lines[label]
            line.successive[line.label[0]] = self.nodes[line.label[0]]
            line.successive[line.label[1]] = self.nodes[line.label[1]]


    def find_paths(self, node1, node2):
        # Given two node labels, this function returns all the paths that connect the two nodes
        # as list of node labels.
        # The admissible paths have to cross any node at most once.
        available_path = []
        for i in range(len(self.nodes.keys()) - 1):
            if i == 0:
                possible_paths = self.generate(node1, self.nodes.keys())
                for path in possible_paths:
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
                out.append(string1+letter)
        return out



    def propagate(self, signal_info):
        # This function has to propagate the signal information through the path specified in it
        # and returns the modified spectral information.
        node = self.nodes[signal_info.path[0]]
        node.propagate(signal_info)

    def draw(self):
        # this function has to draw the network using matplotlib
        # (nodes as dots and connection as lines).
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
