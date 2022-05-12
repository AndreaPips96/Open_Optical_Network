import numpy as np
import scipy.special as sp_spec
import scipy.constants as sp_const

# parameter definition
FREE = 1
OCCUPIED = 0
Nch = 10

BERt = 1e-3             # target Bit Error Rate
Rs = 32 * 1e9           # Symbol rate - 32GHz
Bn = 12.5 * 1e9         # Noise bandwidth - 12.5GHz
CENTER_F = 193.414e12   # C-Band center frequency - 193.414THz
DELTA_F = 50 * 1e9      # Spacing between channels - 50GHz

ALPHA_dB = 0.2          # dB/km
BETA_2 = 2.13e-26       # (m Hz^2)^-1
GAMMA = 1.27e-3         # (Wm)^-1

h_plank = sp_const.h    # Plank constant
c = sp_const.c          # speed of light
pi = sp_const.pi        # Greek pi

DIST_BTW_AMP = 80e3     # Distance between amplifiers - 80km
AMP_GAIN = 16           # Amplifiers gain - 16dB
AMP_NF = 3              # Amplifiers noise figure - 3dB

M_max = 10              # number of Monte Carlo simulations


# method for fixed-rate transceivers' bit rate evaluation
def fixed_bit_rate(gsnr, symbol_rate):
    if gsnr >= 2 * sp_spec.erfcinv(2*BERt)**2 * (symbol_rate/Bn):
        bit_rate = 100e9  # 100Gbps, PM-QPSK
    else:
        bit_rate = 0      # 0Gbps
    return bit_rate


# method for flex-rate transceivers' bit rate evaluation
def flex_bit_rate(gsnr, symbol_rate):
    if gsnr >= 10 * sp_spec.erfcinv((8/3)*BERt)**2 * (symbol_rate/Bn):
        bit_rate = 400e9  # 400Gbps, PM-16QAM
    elif gsnr >= 14/3 * sp_spec.erfcinv((3/2)*BERt)**2 * (symbol_rate/Bn):
        bit_rate = 200e9  # 200Gbps, PM-8QAM
    elif gsnr >= 2 * sp_spec.erfcinv(2*BERt)**2 * (symbol_rate/Bn):
        bit_rate = 100e9  # 100Gbps, PM-QPSK
    else:
        bit_rate = 0      # 0Gbps
    return bit_rate


# method for shannon transceivers' bit rate evaluation
def shannon_bit_rate(gsnr, symbol_rate):
    bit_rate = 2 * symbol_rate * np.log2(1 + (gsnr * symbol_rate / Bn))     # Gbps
    return bit_rate


# method for conversion for ALPHA from linear to dB units
def alpha_lin2db(alpha):
    return alpha * 20 * np.log10(np.exp(1))


# method for conversion for ALPHA from dB to linear units
def alpha_db2lin(alpha_db):
    return alpha_db / (20 * np.log10(np.exp(1)))


# method for conversion from linear to dB units
def lin2db(val):
    return 10 * np.log10(val)


# method for conversion from dB to linear units
def db2lin(val):
    return 10 ** (val/10)


# method for eta_nli evaluation
def eta_nli_eval(alpha_lin, beta_2, gamma, n_channels):
    L_eff = 1 / (2*alpha_lin)
    eta_nli = (16 / (27 * pi)) * \
              np.log(((pi ** 2) / 2) * (beta_2 * (Rs ** 2) / alpha_lin) * (n_channels ** (2 * Rs / DELTA_F))) * \
              (alpha_lin / beta_2) * ((gamma ** 2) * (L_eff ** 2) / (Rs ** 3))
    return eta_nli


# Generate uniform traffic matrix
def generate_traffic_matrix(traffic_matrix, M):
    for node_in in traffic_matrix.index:
        for node_out in traffic_matrix.columns:
            # No traffic from a node to itself is admitted
            if node_in != node_out:
                traffic_matrix[node_in][node_out] = 100e9 * M   # Gbps
            else:
                traffic_matrix[node_in][node_out] = 0
    return traffic_matrix


# Evaluate overall congestion percentage
def congestion_eval(Network):
    tot_perc = 0
    for node in Network.nodes.keys():
        for channels in Network.nodes[node].switching_matrix.values():
            available_ch = np.sum(list(channels.values())) / Nch
            tot_node_ch = len(list(channels.values()))**2
            tot_perc += (available_ch/tot_node_ch)*100
            break
    tot_perc = tot_perc/len(Network.nodes.keys())
    return tot_perc
