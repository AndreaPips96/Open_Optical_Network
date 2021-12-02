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
        # if node1 in self.nodes.keys() & node2 in self.nodes.keys():
        #     source = self.nodes[node1]
        #     dest = self.nodes[node2]

        paths = []
        index = 0
        for label1 in self.nodes[node1].connected_nodes:
            if label1 == node2:
                paths.append(node1 + label1)  # direct link between node1 and node2
            else:
                crossed = node1 + label1
                for label2 in self.nodes[label1].connected_nodes:
                    if label2 == node2:
                        crossed = crossed + label2
                        paths.append(crossed)
                    elif label2 in crossed:
                        pass
                    else:
                        crossed = node1 + label1 + label2
                        for label3 in self.nodes[label2].connected_nodes:
                            if label3 == node2:
                                paths.append(crossed + label3)
                            elif label2 in crossed:
                                pass
                            else:
                                pass
        return paths




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
