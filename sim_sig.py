# sim_sig.py
"""
Generates simulated signal for FSK testing
Modulateds the signal and writes to .wav file
"""

import numpy as np
import matplotlib.pyplot as pyplot

Fs   = 860.0  # sampling frequency 
Fc   = 250.0  # carrier frequency
Fdev = 50.0   # deviation from carrier frequency for FSK 
bitrate = 20.0  # bits/sec
samp_per_bit = int(Fs/bitrate)  # duration of one representation 
numbits = 32
duration = samp_per_bit * numbits  # duration of whole signal in samples



# generate random bits
bits = np.random.random_integers(0, 1, numbits)

# Voltage Control Oscillator (VCO)  
m = []
for bit in bits:
    if bit == 0:
        m += [Fc-Fdev]*samp_per_bit
    else:
        m += [Fc+Fdev]*samp_per_bit
   
# array for easy operations
m = np.array(m)

# Generate Carrier Frequency 
t = np.arange(0, numbits/bitrate , 1/Fs, dtype=np.float)  # time vector
print len(m), len(t)

amp = 1
carrier = amp*np.cos(2*np.pi * m * t)

amp_noise = 0.1
noise = np.random.randn(len(carrier)+1)*amp_noise
# add Gaussian white noise to carrier signal
carrier = np.add(carrier, noise)
'''
pyplot.subplot(2,1,1)
pyplot.plot(carrier)
pyplot.subplot(2,1,2)
pyplot.plot(bits)
pyplot.show()
'''

