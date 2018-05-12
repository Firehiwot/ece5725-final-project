#
# sim_fsk_decoder.py
# Angus Gibbs (aag233) and Joao Pedro Carvao (jc2697)
#
# Demodulates signal using FSK
#

import matplotlib.pyplot as pyplot
import scipy.signal.signaltools as sigtool
import scipy.signal as signal 
import numpy as np

from sim_fsk_encoder import *

# Differentiate received carrier signal
carrier_diff = np.diff(carrier, 1)

# Detect envelope to extract digital data 
carrier_env = np.abs(sigtool.hilbert(carrier_diff))

# Create low pass filter
lpf = signal.firwin(numtaps=100, cutoff=bitrate*2, nyq=Fs/2)

# Filter our signal 
carrier_filtered = signal.lfilter( lpf, 1.0, carrier_env)

# Slice to ones and zeros to extract original bits
mean = np.mean(carrier_filtered)
rx_data = []
sampled_signal = carrier_filtered[int(Fs/bitrate/2) : len(carrier_filtered) : int(Fs/bitrate)]
for bit in sampled_signal: 
  if bit > mean: 
    rx_data.append(1)
  else: 
    rx_data.append(0)

# Output the sent and received bits
print "inbits: "+str(bits)
print "outbits: "+str(np.array(rx_data))

# Calculate the bit error rate
biterror = 0
for i, bit in enumerate(bits):
    if bit != rx_data[i]:
        biterror += 1
print biterror
