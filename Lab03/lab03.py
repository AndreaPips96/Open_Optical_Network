# USEFUL CLASSES
import scipy.constants as sp
import numpy as np

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
        self.path = path.pop(0)
        return self.path

class Node:

    def __init__(self, label, dictionary):
        self.label = label                                      # string
        self.position = dictionary["position"]                  # tuple(float, float)
        self.connected_nodes = dictionary["connected_nodes"]    # list[string]
        self.successive = {}                                    # dict[Line]

    def propagate(self):
        SignalInformation.update_path()



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
        signal_info.update_powlat(0,self.noise_generation(signal_info.signal_power),self.latency_generation())


class Network:

    def __init__(self, my_dict):
        self.nodes = {}
        self.lines = {}

        for key in my_dict:
            self.nodes[key] = Node.__init__(key, key, my_dict[key])

        for key in self.nodes:
            for element in self.nodes[key].connected_nodes:
                distance = np.sqrt(self.nodes[key].position(0)-self.nodes[element].position(0) + self.nodes[key].position(1)-self.nodes[element].position(1))
                line_label = (key + element)
                self.lines[line_label] = Line.__init__(line_label, line_label, distance)


    def connect(self):
        pass

    def find_paths(self, node1, node2):
        # given two node labels, this function returns all the paths that connect the two nodes
        # as list of node labels.
        # The admissible paths have to cross any node at most once;
        pass

    def propagate(self, signal_information):
        # this function has to propagate the
        # signal information through the path specified in it and returns the
        # modified spectral information;
        pass

    def draw(self):
        # this function has to draw the network using matplotlib
        # (nodes as dots and connection as lines).
        pass