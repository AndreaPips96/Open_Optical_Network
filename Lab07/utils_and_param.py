import numpy as np
import scipy.special as sp_spec

# parameter definition
free = 1
occupied = 0
BERt = 1e-3
Rs = 32 * 1e9       # 32GHz
Bn = 12.5 * 1e9     # 12.5GHz


# method for fixed-rate transceivers' bit rate evaluation
def fixed_bit_rate(gsnr):
    if gsnr >= 2 * sp_spec.erfcinv(2*BERt )**2 * (Rs/Bn):
        Rb = 100e9  # 100Gbps, PM-QPSK
    else:
        Rb = 0      # 0Gbps
    return Rb


# method for flex-rate transceivers' bit rate evaluation
def flex_bit_rate(gsnr):
    if gsnr >= 10 * sp_spec.erfcinv((8/3)*BERt)**2 * (Rs/Bn):
        Rb = 400e9  # 400Gbps, PM-16QAM
    elif gsnr >= 14/3 * sp_spec.erfcinv((3/2)*BERt)**2 * (Rs/Bn):
        Rb = 200e9  # 200Gbps, PM-8QAM
    elif gsnr >= 2 * sp_spec.erfcinv(2*BERt)**2 * (Rs/Bn):
        Rb = 100e9  # 100Gbps, PM-QPSK
    else:
        Rb = 0      # 0Gbps
    return Rb


# method for shannon transceivers' bit rate evaluation
def shannon_bit_rate(gsnr):
    Rb = 2 * Rs * np.log2(1 + (gsnr * Rs / Bn))     # Gbps
    return Rb
