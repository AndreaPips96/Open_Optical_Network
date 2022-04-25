import numpy as np
import scipy.special as sp_spec
import scipy.constants as sp_const

# parameter definition
FREE = 1
OCCUPIED = 0

BERt = 1e-3
Rs = 32 * 1e9           # Symbol rate - 32GHz
Bn = 12.5 * 1e9         # Noise bandwidth - 12.5GHz
CENTER_F = 193.414e12   # C-Band center frequency - 193.414THz
DELTA_F = 50 * 1e9      # Spacing between channels - 50GHz

ALPHA_dB = 0.2          # dB/km
BETA_2 = 2.13e-26       # (m Hz^2)^-1 = ps^2/km
GAMMA = 1.27e-3         # (Wm)^-1

h_plank = sp_const.h    # Plank constant
c = sp_const.c          # speed of light
pi = sp_const.pi        # Greek pi

DIST_BTW_AMP = 80e3     # Distance between amplifiers - 80e3m = 80km
AMP_GAIN = 16           # Amplifiers gain - 16dB
AMP_NF = 3             # Amplifiers noise figure - 3dB


# method for fixed-rate transceivers' bit rate evaluation
def fixed_bit_rate(gsnr):
    if gsnr >= 2 * sp_spec.erfcinv(2*BERt )**2 * (Rs/Bn):
        bit_rate = 100e9  # 100Gbps, PM-QPSK
    else:
        bit_rate = 0      # 0Gbps
    return bit_rate


# method for flex-rate transceivers' bit rate evaluation
def flex_bit_rate(gsnr):
    if gsnr >= 10 * sp_spec.erfcinv((8/3)*BERt)**2 * (Rs/Bn):
        bit_rate = 400e9  # 400Gbps, PM-16QAM
    elif gsnr >= 14/3 * sp_spec.erfcinv((3/2)*BERt)**2 * (Rs/Bn):
        bit_rate = 200e9  # 200Gbps, PM-8QAM
    elif gsnr >= 2 * sp_spec.erfcinv(2*BERt)**2 * (Rs/Bn):
        bit_rate = 100e9  # 100Gbps, PM-QPSK
    else:
        bit_rate = 0      # 0Gbps
    return bit_rate


# method for shannon transceivers' bit rate evaluation
def shannon_bit_rate(gsnr):
    bit_rate = 2 * Rs * np.log2(1 + (gsnr * Rs / Bn))     # Gbps
    return bit_rate


# method for conversion for ALPHA from lin to dB
def alpha_lin2db(alpha):
    return alpha * 20 * np.log10(np.exp(1))


# method for conversion for ALPHA from dB to lin
def alpha_db2lin(alpha_db):
    return alpha_db / (20 * np.log10(np.exp(1)))
